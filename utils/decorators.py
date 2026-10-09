from functools import wraps
from flask import flash, redirect, url_for, request, jsonify, abort
from flask_login import current_user

def role_required(*allowed_roles):
    """
    Decorator to restrict access to users with specified roles.
    Allowed roles: 'Admin', 'Manager', 'Employee'
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'error': 'Unauthorized', 'message': 'Please log in to continue.'}), 401
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login', next=request.url))

            if current_user.role not in allowed_roles:
                if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'error': 'Forbidden', 'message': 'You do not have permission to perform this action.'}), 403
                flash('You do not have permission to access that resource.', 'danger')
                return redirect(url_for('dashboard.index'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Convenience decorator for admin-only routes."""
    return role_required('Admin')(f)

def manager_or_admin_required(f):
    """Convenience decorator for Manager and Admin routes."""
    return role_required('Admin', 'Manager')(f)

