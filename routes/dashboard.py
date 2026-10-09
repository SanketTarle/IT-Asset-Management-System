from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from utils.database import db
from models.asset import Asset
from models.category import Category
from models.employee import Employee
from models.assignment import AssetAssignment
from models.maintenance import MaintenanceRecord
from models.transaction import AssetTransaction

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    # If the user is an Employee, let's also pass employee-specific context
    user_employee = Employee.query.filter_by(email=current_user.email).first()
    my_assets = []
    if user_employee:
        my_assets = Asset.query.filter_by(assigned_to=user_employee.id).all()

    # KPI Metrics
    total_assets = Asset.query.count()
    assigned_assets = Asset.query.filter_by(status='Assigned').count()
    available_assets = Asset.query.filter_by(status='Available').count()
    maintenance_assets = Asset.query.filter_by(status='Under Maintenance').count()
    retired_assets = Asset.query.filter(Asset.status.in_(['Retired', 'Disposed'])).count()
    active_assets = total_assets - retired_assets
    total_employees = Employee.query.count()

    total_value = db.session.query(func.sum(Asset.current_value)).scalar() or 0.0
    total_purchase_value = db.session.query(func.sum(Asset.purchase_price)).scalar() or 0.0
    total_maintenance_cost = db.session.query(func.sum(MaintenanceRecord.cost)).scalar() or 0.0

    # Recent Records
    recent_assets = Asset.query.order_by(Asset.id.desc()).limit(5).all()
    recent_assignments = AssetAssignment.query.order_by(AssetAssignment.id.desc()).limit(5).all()
    recent_transactions = AssetTransaction.query.order_by(AssetTransaction.id.desc()).limit(8).all()
    recent_maintenance = MaintenanceRecord.query.order_by(MaintenanceRecord.id.desc()).limit(5).all()

    return render_template(
        'dashboard.html',
        total_assets=total_assets,
        active_assets=active_assets,
        assigned_assets=assigned_assets,
        available_assets=available_assets,
        maintenance_assets=maintenance_assets,
        retired_assets=retired_assets,
        total_employees=total_employees,
        total_value=total_value,
        total_purchase_value=total_purchase_value,
        total_maintenance_cost=total_maintenance_cost,
        recent_assets=recent_assets,
        recent_assignments=recent_assignments,
        recent_transactions=recent_transactions,
        recent_maintenance=recent_maintenance,
        my_assets=my_assets,
        user_employee=user_employee
    )

@dashboard_bp.route('/api/dashboard-charts')
@login_required
def dashboard_charts():
    # 1. Assets by Category
    cat_counts = db.session.query(Category.name, func.count(Asset.id))\
        .outerjoin(Asset, Category.id == Asset.category_id)\
        .group_by(Category.name).all()
    
    cat_labels = [c[0] for c in cat_counts]
    cat_values = [c[1] for c in cat_counts]

    # 2. Assets by Status
    status_counts = db.session.query(Asset.status, func.count(Asset.id))\
        .group_by(Asset.status).all()
    status_labels = [s[0] for s in status_counts]
    status_values = [s[1] for s in status_counts]

    # 3. Assets by Condition
    condition_counts = db.session.query(Asset.condition, func.count(Asset.id))\
        .group_by(Asset.condition).all()
    condition_labels = [c[0] for c in condition_counts]
    condition_values = [c[1] for c in condition_counts]

    # 4. Asset Value by Category
    cat_values_query = db.session.query(Category.name, func.sum(Asset.current_value))\
        .join(Asset, Category.id == Asset.category_id)\
        .group_by(Category.name).all()
    value_labels = [c[0] for c in cat_values_query]
    value_amounts = [round(c[1] or 0.0, 2) for c in cat_values_query]

    # 5. Maintenance Cost by Category
    maint_by_cat = db.session.query(Category.name, func.sum(MaintenanceRecord.cost))\
        .join(Asset, Category.id == Asset.category_id)\
        .join(MaintenanceRecord, Asset.id == MaintenanceRecord.asset_id)\
        .group_by(Category.name).all()
    maint_labels = [m[0] for m in maint_by_cat]
    maint_amounts = [round(m[1] or 0.0, 2) for m in maint_by_cat]

    return jsonify({
        'categories': {'labels': cat_labels, 'values': cat_values},
        'statuses': {'labels': status_labels, 'values': status_values},
        'conditions': {'labels': condition_labels, 'values': condition_values},
        'values_by_category': {'labels': value_labels, 'values': value_amounts},
        'maintenance_by_category': {'labels': maint_labels, 'values': maint_amounts}
    })

