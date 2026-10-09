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

__all__ = [
    'auth_bp',
    'dashboard_bp',
    'assets_bp',
    'employees_bp',
    'categories_bp',
    'locations_bp',
    'assignments_bp',
    'maintenance_bp',
    'reports_bp',
    'settings_bp'
]

