import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash
from utils.database import db
from utils.decorators import admin_required
from models.user import User
from models.asset import Asset
from models.employee import Employee
from models.category import Category
from models.location import Location
from models.maintenance import MaintenanceRecord
from models.assignment import AssetAssignment

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not name:
            flash('Name cannot be empty.', 'danger')
            return redirect(url_for('settings.profile'))

        current_user.name = name

        # Password update if requested
        if current_password or new_password:
            if not current_user.check_password(current_password):
                flash('Current password is incorrect.', 'danger')
                return redirect(url_for('settings.profile'))

            if len(new_password) < 6:
                flash('New password must be at least 6 characters.', 'danger')
                return redirect(url_for('settings.profile'))

            if new_password != confirm_password:
                flash('New passwords do not match.', 'danger')
                return redirect(url_for('settings.profile'))

            current_user.set_password(new_password)
            flash('Your password has been changed successfully.', 'success')

        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('settings.profile'))

    return render_template('profile.html')

@settings_bp.route('/settings')
@login_required
@admin_required
def settings_page():
    users = User.query.order_by(User.id).all()
    
    # System statistics
    db_path = os.path.join(current_app.root_path, 'database.db')
    db_size_kb = 0
    if os.path.exists(db_path):
        db_size_kb = round(os.path.getsize(db_path) / 1024, 2)

    stats = {
        'database_file': 'database.db',
        'database_size_kb': db_size_kb,
        'users_count': User.query.count(),
        'assets_count': Asset.query.count(),
        'employees_count': Employee.query.count(),
        'categories_count': Category.query.count(),
        'locations_count': Location.query.count(),
        'assignments_count': AssetAssignment.query.count(),
        'maintenance_count': MaintenanceRecord.query.count()
    }

    return render_template('settings.html', users=users, stats=stats)

@settings_bp.route('/settings/users/add', methods=['POST'])
@login_required
@admin_required
def add_user():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')
    role = request.form.get('role', 'Employee')

    if not name or not email or not password:
        flash('All fields are required.', 'danger')
        return redirect(url_for('settings.settings_page'))

    if User.query.filter_by(email=email).first():
        flash(f'User with email "{email}" already exists.', 'danger')
        return redirect(url_for('settings.settings_page'))

    user = User(name=name, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    flash(f'User "{name}" ({role}) added successfully.', 'success')
    return redirect(url_for('settings.settings_page'))

@settings_bp.route('/settings/users/<int:user_id>/role', methods=['POST'])
@login_required
@admin_required
def update_user_role(user_id):
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')

    if user.id == current_user.id and new_role != 'Admin':
        flash('You cannot remove the Admin role from your own current account.', 'danger')
        return redirect(url_for('settings.settings_page'))

    if new_role in ['Admin', 'Manager', 'Employee']:
        user.role = new_role
        db.session.commit()
        flash(f'Role for {user.name} changed to {new_role}.', 'success')
    else:
        flash('Invalid role specified.', 'danger')

    return redirect(url_for('settings.settings_page'))

@settings_bp.route('/settings/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('settings.settings_page'))

    name = user.name
    db.session.delete(user)
    db.session.commit()
    flash(f'User "{name}" has been deleted.', 'info')
    return redirect(url_for('settings.settings_page'))

@settings_bp.route('/settings/backup-db')
@login_required
@admin_required
def backup_database():
    db_path = os.path.join(current_app.root_path, 'database.db')
    if not os.path.exists(db_path):
        flash('Database file not found.', 'danger')
        return redirect(url_for('settings.settings_page'))

    return send_file(
        db_path,
        as_attachment=True,
        download_name=f"database_backup_{os.path.basename(db_path)}"
    )

