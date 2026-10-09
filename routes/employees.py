from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_
from utils.database import db
from utils.decorators import role_required, admin_required, manager_or_admin_required
from utils.helpers import generate_employee_code
from models.employee import Employee
from models.location import Location
from models.asset import Asset
from models.assignment import AssetAssignment

employees_bp = Blueprint('employees', __name__, url_prefix='/employees')

@employees_bp.route('/')
@login_required
def index():
    query = Employee.query

    q = request.args.get('q', '').strip()
    if q:
        query = query.filter(
            or_(
                Employee.employee_code.ilike(f'%{q}%'),
                Employee.name.ilike(f'%{q}%'),
                Employee.email.ilike(f'%{q}%'),
                Employee.department.ilike(f'%{q}%'),
                Employee.designation.ilike(f'%{q}%')
            )
        )

    department = request.args.get('department', '').strip()
    if department:
        query = query.filter(Employee.department == department)

    status = request.args.get('status', '').strip()
    if status:
        query = query.filter(Employee.status == status)

    employees = query.order_by(Employee.name).all()
    departments = [d[0] for d in db.session.query(Employee.department).distinct() if d[0]]

    return render_template(
        'employees.html',
        employees=employees,
        departments=departments,
        q=q,
        selected_department=department,
        selected_status=status
    )

@employees_bp.route('/add', methods=['GET', 'POST'])
@login_required
@manager_or_admin_required
def add():
    locations = Location.query.order_by(Location.name).all()

    if request.method == 'POST':
        employee_code = request.form.get('employee_code', '').strip()
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        department = request.form.get('department', '').strip()
        designation = request.form.get('designation', '').strip()
        location_id = request.form.get('location_id', type=int) or None
        status = request.form.get('status', 'Active')

        if not name or not email:
            flash('Employee name and email are required.', 'danger')
            return render_template('employees.html', locations=locations, employees=Employee.query.all())

        if not employee_code:
            employee_code = generate_employee_code()

        if Employee.query.filter_by(employee_code=employee_code).first():
            flash(f'Employee code "{employee_code}" already exists.', 'danger')
            return redirect(url_for('employees.index'))

        if Employee.query.filter_by(email=email).first():
            flash(f'An employee with email "{email}" already exists.', 'danger')
            return redirect(url_for('employees.index'))

        employee = Employee(
            employee_code=employee_code,
            name=name,
            email=email,
            phone=phone,
            department=department,
            designation=designation,
            location_id=location_id,
            status=status
        )
        db.session.add(employee)
        db.session.commit()

        flash(f'Employee "{name}" ({employee_code}) added successfully!', 'success')
        return redirect(url_for('employees.details', employee_id=employee.id))

    suggested_code = generate_employee_code()
    return redirect(url_for('employees.index'))

@employees_bp.route('/<int:employee_id>')
@login_required
def details(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    assigned_assets = Asset.query.filter_by(assigned_to=employee.id).all()
    assignments_history = AssetAssignment.query.filter_by(employee_id=employee.id)\
        .order_by(AssetAssignment.id.desc()).all()
    locations = Location.query.order_by(Location.name).all()

    return render_template(
        'employee_details.html',
        employee=employee,
        assigned_assets=assigned_assets,
        assignments_history=assignments_history,
        locations=locations
    )

@employees_bp.route('/<int:employee_id>/edit', methods=['POST'])
@login_required
@manager_or_admin_required
def edit(employee_id):
    employee = Employee.query.get_or_404(employee_id)

    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()
    phone = request.form.get('phone', '').strip()
    department = request.form.get('department', '').strip()
    designation = request.form.get('designation', '').strip()
    location_id = request.form.get('location_id', type=int) or None
    status = request.form.get('status', employee.status)

    if not name or not email:
        flash('Employee name and email are required.', 'danger')
        return redirect(url_for('employees.details', employee_id=employee.id))

    # Check email duplicate if changed
    if email != employee.email:
        existing = Employee.query.filter_by(email=email).first()
        if existing:
            flash(f'Email "{email}" is already used by another employee.', 'danger')
            return redirect(url_for('employees.details', employee_id=employee.id))

    employee.name = name
    employee.email = email
    employee.phone = phone
    employee.department = department
    employee.designation = designation
    employee.location_id = location_id
    employee.status = status

    db.session.commit()
    flash(f'Employee "{employee.name}" updated successfully.', 'success')
    return redirect(url_for('employees.details', employee_id=employee.id))

@employees_bp.route('/<int:employee_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(employee_id):
    employee = Employee.query.get_or_404(employee_id)

    # Check if employee has active assigned assets
    active_assets = Asset.query.filter_by(assigned_to=employee.id).all()
    if active_assets:
        flash(f'Cannot delete employee "{employee.name}" because they have {len(active_assets)} active assigned assets. Please return the assets first.', 'danger')
        return redirect(url_for('employees.details', employee_id=employee.id))

    name = employee.name
    db.session.delete(employee)
    db.session.commit()

    flash(f'Employee "{name}" deleted successfully.', 'info')
    return redirect(url_for('employees.index'))

