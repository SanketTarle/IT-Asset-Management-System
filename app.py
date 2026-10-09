import os
from flask import Flask, render_template
from flask_login import LoginManager
from config import Config
from utils.database import db, init_db
from models.user import User

# Import Blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.assets import assets_bp
from routes.employees import employees_bp
from routes.categories import categories_bp
from routes.locations import locations_bp
from routes.assignments import assignments_bp
from routes.maintenance import maintenance_bp
from routes.reports import reports_bp
from routes.settings import settings_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(assets_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(locations_bp)
    app.register_blueprint(assignments_bp)
    app.register_blueprint(maintenance_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)

    # Custom Jinja Template Filters
    @app.template_filter('currency')
    def currency_filter(value):
        try:
            return f"${float(value):,.2f}"
        except (ValueError, TypeError):
            return "$0.00"

    @app.template_filter('format_date')
    def format_date_filter(value, fmt='%b %d, %Y'):
        if not value:
            return '—'
        try:
            return value.strftime(fmt)
        except Exception:
            return str(value)

    # Context Processor for Global Variables
    @app.context_processor
    def inject_globals():
        from datetime import date
        today_date = date.today()
        return {
            'app_name': 'Asset Management System',
            'app_version': '1.0.0',
            'company_name': 'Enterprise Corp',
            'today': today_date,
            'today_str': today_date.strftime('%Y-%m-%d')
        }

    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('404.html', message="Forbidden: You do not have permission to view this resource."), 403

    # Automatic Database Initialization (database.db created on first run)
    init_db(app)

    return app

app = create_app()

if __name__ == '__main__':
    # Starts server on 127.0.0.1:5000
    print("=" * 60)
    print("[AMS] Asset Management System starting...")
    print("[AMS] URL: http://127.0.0.1:5000")
    print("[AMS] Default Admin: admin@company.com | Password: Admin@123")
    print("=" * 60)
    app.run(host='127.0.0.1', port=5000, debug=True)
