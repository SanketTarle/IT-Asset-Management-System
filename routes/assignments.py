from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_
from utils.database import db
from utils.decorators import manager_or_admin_required
from utils.helpers import parse_date, log_transaction
from models.assignment import AssetAssignment
from models.asset import Asset
from models.employee import Employee

assignments_bp = Blueprint('assignments', __name__, url_prefix='/assignments')

@assignments_bp.route('/')
@login_required
def index():
    status = request.args.get('status', '').strip()  # Active, Returned
    query = AssetAssignment.query

    if status:
        query = query.filter(AssetAssignment.assignment_status == status)

    assignments = query.order_by(AssetAssignment.id.desc()).all()
    
    # Available assets for assignment modal
    available_assets = Asset.query.filter_by(status='Available').order_by(Asset.name).all()
    employees = Employee.query.filter_by(status='Active').order_by(Employee.name).all()

    active_count = AssetAssignment.query.filter_by(assignment_status='Active').count()
    returned_count = AssetAssignment.query.filter_by(assignment_status='Returned').count()

    return render_template(
        'assignments.html',
        assignments=assignments,
        available_assets=available_assets,
        employees=employees,
        selected_status=status,
        active_count=active_count,
        returned_count=returned_count
    )

@assignments_bp.route('/assign', methods=['POST'])
@login_required
@manager_or_admin_required
def create_assignment():
    asset_id = request.form.get('asset_id', type=int)
    employee_id = request.form.get('employee_id', type=int)
    assigned_date_str = request.form.get('assigned_date', '').strip()
    notes = request.form.get('notes', '').strip()

    if not asset_id or not employee_id:
        flash('Please select both an asset and an employee.', 'danger')
        return redirect(url_for('assignments.index'))

    asset = Asset.query.get_or_404(asset_id)
    employee = Employee.query.get_or_404(employee_id)
    assigned_date = parse_date(assigned_date_str) or date.today()

    if asset.status == 'Assigned' and asset.assigned_to:
        flash(f'Asset "{asset.name}" is already assigned to {asset.assigned_employee.name}. Return it first.', 'warning')
        return redirect(url_for('assignments.index'))

    assignment = AssetAssignment(
        asset_id=asset.id,
        employee_id=employee.id,
        assigned_date=assigned_date,
        assignment_status='Active',
        notes=notes
    )
    db.session.add(assignment)

    asset.status = 'Assigned'
    asset.assigned_to = employee.id
    db.session.commit()

    log_transaction(
        asset_id=asset.id,
        transaction_type='Assignment',
        old_value='Available',
        new_value=f'Assigned to {employee.name}',
        performed_by=current_user.email,
        notes=notes or 'Asset assigned via Assignments portal'
    )

    flash(f'Asset "{asset.name}" successfully assigned to {employee.name}.', 'success')
    return redirect(url_for('assignments.index'))

@assignments_bp.route('/<int:assignment_id>/return', methods=['POST'])
@login_required
@manager_or_admin_required
def return_assignment(assignment_id):
    assignment = AssetAssignment.query.get_or_404(assignment_id)
    returned_date_str = request.form.get('returned_date', '').strip()
    notes = request.form.get('notes', '').strip()
    condition = request.form.get('condition', assignment.asset.condition)

    returned_date = parse_date(returned_date_str) or date.today()

    assignment.returned_date = returned_date
    assignment.assignment_status = 'Returned'
    if notes:
        assignment.notes = (assignment.notes or '') + f' | Return: {notes}'

    asset = assignment.asset
    asset.status = 'Available'
    asset.assigned_to = None
    asset.condition = condition

    db.session.commit()

    log_transaction(
        asset_id=asset.id,
        transaction_type='Return',
        old_value=f'Assigned to {assignment.employee.name}',
        new_value='Available',
        performed_by=current_user.email,
        notes=f"Returned on {returned_date}. Condition: {condition}. {notes}"
    )

    flash(f'Asset "{asset.name}" marked as returned and is now Available.', 'success')
    return redirect(url_for('assignments.index'))

