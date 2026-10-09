from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import or_, desc, asc
from utils.database import db
from utils.decorators import role_required, admin_required, manager_or_admin_required
from utils.helpers import (
    generate_asset_code,
    save_asset_image,
    log_transaction,
    parse_date
)
from models.asset import Asset
from models.category import Category
from models.location import Location
from models.employee import Employee
from models.assignment import AssetAssignment
from models.maintenance import MaintenanceRecord

assets_bp = Blueprint('assets', __name__, url_prefix='/assets')

@assets_bp.route('/')
@login_required
def index():
    # If Employee, only show their assigned assets or all with read-only depending on role
    query = Asset.query

    # Search query
    q = request.args.get('q', '').strip()
    if q:
        search_filter = or_(
            Asset.asset_code.ilike(f'%{q}%'),
            Asset.name.ilike(f'%{q}%'),
            Asset.serial_number.ilike(f'%{q}%'),
            Asset.manufacturer.ilike(f'%{q}%'),
            Asset.model.ilike(f'%{q}%')
        )
        query = query.filter(search_filter)

    # Filters
    category_id = request.args.get('category_id', type=int)
    if category_id:
        query = query.filter(Asset.category_id == category_id)

    status = request.args.get('status', '').strip()
    if status:
        query = query.filter(Asset.status == status)

    condition = request.args.get('condition', '').strip()
    if condition:
        query = query.filter(Asset.condition == condition)

    location_id = request.args.get('location_id', type=int)
    if location_id:
        query = query.filter(Asset.location_id == location_id)

    employee_id = request.args.get('employee_id', type=int)
    if employee_id:
        query = query.filter(Asset.assigned_to == employee_id)

    # Sorting
    sort_by = request.args.get('sort_by', 'id')
    sort_dir = request.args.get('sort_dir', 'desc')
    
    sort_column = getattr(Asset, sort_by, Asset.id)
    if sort_dir == 'asc':
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    assets = query.all()

    # Auxiliary data for filter dropdowns
    categories = Category.query.order_by(Category.name).all()
    locations = Location.query.order_by(Location.name).all()
    employees = Employee.query.filter_by(status='Active').order_by(Employee.name).all()

    return render_template(
        'assets.html',
        assets=assets,
        categories=categories,
        locations=locations,
        employees=employees,
        q=q,
        selected_category=category_id,
        selected_status=status,
        selected_condition=condition,
        selected_location=location_id,
        selected_employee=employee_id,
        sort_by=sort_by,
        sort_dir=sort_dir
    )

@assets_bp.route('/add', methods=['GET', 'POST'])
@login_required
@manager_or_admin_required
def add():
    categories = Category.query.order_by(Category.name).all()
    locations = Location.query.order_by(Location.name).all()
    employees = Employee.query.filter_by(status='Active').order_by(Employee.name).all()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category_id = request.form.get('category_id', type=int)
        asset_code = request.form.get('asset_code', '').strip()
        serial_number = request.form.get('serial_number', '').strip() or None
        manufacturer = request.form.get('manufacturer', '').strip()
        model = request.form.get('model', '').strip()
        location_id = request.form.get('location_id', type=int) or None
        purchase_date_str = request.form.get('purchase_date', '').strip()
        warranty_expiry_str = request.form.get('warranty_expiry', '').strip()
        supplier = request.form.get('supplier', '').strip()
        status = request.form.get('status', 'Available')
        condition = request.form.get('condition', 'Good')
        description = request.form.get('description', '').strip()
        notes = request.form.get('notes', '').strip()
        assigned_to = request.form.get('assigned_to', type=int) or None

        try:
            purchase_price = float(request.form.get('purchase_price') or 0.0)
        except ValueError:
            purchase_price = 0.0

        try:
            current_value = float(request.form.get('current_value') or purchase_price)
        except ValueError:
            current_value = purchase_price

        if not name or not category_id:
            flash('Asset name and category are required.', 'danger')
            return render_template('asset_form.html', action='add', categories=categories, locations=locations, employees=employees, asset=request.form)

        # Generate asset code if not specified
        if not asset_code:
            asset_code = generate_asset_code()
        else:
            existing = Asset.query.filter_by(asset_code=asset_code).first()
            if existing:
                flash(f'Asset code "{asset_code}" is already in use. A new unique code has been generated.', 'warning')
                asset_code = generate_asset_code()

        # Check unique serial number
        if serial_number:
            existing_sn = Asset.query.filter_by(serial_number=serial_number).first()
            if existing_sn:
                flash(f'An asset with serial number "{serial_number}" already exists ({existing_sn.name} - {existing_sn.asset_code}).', 'danger')
                return render_template('asset_form.html', action='add', categories=categories, locations=locations, employees=employees, asset=request.form)

        # Handle image upload
        image_file = request.files.get('image')
        image_name = save_asset_image(image_file)

        # If assigned_to is specified, update status to Assigned
        if assigned_to:
            status = 'Assigned'

        asset = Asset(
            asset_code=asset_code,
            name=name,
            category_id=category_id,
            description=description,
            manufacturer=manufacturer,
            model=model,
            serial_number=serial_number,
            purchase_date=parse_date(purchase_date_str),
            purchase_price=purchase_price,
            current_value=current_value,
            warranty_expiry=parse_date(warranty_expiry_str),
            supplier=supplier,
            location_id=location_id,
            status=status,
            condition=condition,
            assigned_to=assigned_to,
            image=image_name,
            notes=notes
        )

        db.session.add(asset)
        db.session.commit()

        # If assigned right upon creation, create assignment record
        if assigned_to:
            emp = db.session.get(Employee, assigned_to)
            asgn = AssetAssignment(
                asset_id=asset.id,
                employee_id=assigned_to,
                assigned_date=date.today(),
                assignment_status='Active',
                notes='Assigned during initial asset registration'
            )
            db.session.add(asgn)
            db.session.commit()

        # Log transaction
        log_transaction(
            asset_id=asset.id,
            transaction_type='Registration',
            old_value=None,
            new_value=asset.status,
            performed_by=current_user.email,
            notes=f"New asset registered by {current_user.name}"
        )

        flash(f'Asset "{asset.name}" ({asset.asset_code}) created successfully!', 'success')
        return redirect(url_for('assets.details', asset_id=asset.id))

    # GET request - generate prospective asset code
    suggested_code = generate_asset_code()
    return render_template(
        'asset_form.html',
        action='add',
        suggested_code=suggested_code,
        categories=categories,
        locations=locations,
        employees=employees,
        asset={}
    )

@assets_bp.route('/<int:asset_id>')
@login_required
def details(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    employees = Employee.query.filter_by(status='Active').order_by(Employee.name).all()
    assignments = asset.assignments.all()
    maintenance_records = asset.maintenance_records.all()
    transactions = asset.transactions.all()

    return render_template(
        'asset_details.html',
        asset=asset,
        employees=employees,
        assignments=assignments,
        maintenance_records=maintenance_records,
        transactions=transactions
    )

@assets_bp.route('/<int:asset_id>/edit', methods=['GET', 'POST'])
@login_required
@manager_or_admin_required
def edit(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    categories = Category.query.order_by(Category.name).all()
    locations = Location.query.order_by(Location.name).all()
    employees = Employee.query.filter_by(status='Active').order_by(Employee.name).all()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category_id = request.form.get('category_id', type=int)
        serial_number = request.form.get('serial_number', '').strip() or None
        manufacturer = request.form.get('manufacturer', '').strip()
        model = request.form.get('model', '').strip()
        location_id = request.form.get('location_id', type=int) or None
        purchase_date_str = request.form.get('purchase_date', '').strip()
        warranty_expiry_str = request.form.get('warranty_expiry', '').strip()
        supplier = request.form.get('supplier', '').strip()
        condition = request.form.get('condition', asset.condition)
        description = request.form.get('description', '').strip()
        notes = request.form.get('notes', '').strip()

        try:
            purchase_price = float(request.form.get('purchase_price') or 0.0)
        except ValueError:
            purchase_price = asset.purchase_price

        try:
            current_value = float(request.form.get('current_value') or purchase_price)
        except ValueError:
            current_value = asset.current_value

        if not name or not category_id:
            flash('Asset name and category are required.', 'danger')
            return render_template('asset_form.html', action='edit', asset=asset, categories=categories, locations=locations, employees=employees)

        # Check unique serial number if changed
        if serial_number and serial_number != asset.serial_number:
            existing_sn = Asset.query.filter_by(serial_number=serial_number).first()
            if existing_sn:
                flash(f'An asset with serial number "{serial_number}" already exists.', 'danger')
                return render_template('asset_form.html', action='edit', asset=asset, categories=categories, locations=locations, employees=employees)

        # Handle image upload
        image_file = request.files.get('image')
        new_image = save_asset_image(image_file)
        if new_image:
            asset.image = new_image

        old_val_summary = f"Val: ${asset.current_value}, Cond: {asset.condition}"

        asset.name = name
        asset.category_id = category_id
        asset.serial_number = serial_number
        asset.manufacturer = manufacturer
        asset.model = model
        asset.location_id = location_id
        asset.purchase_date = parse_date(purchase_date_str)
        asset.purchase_price = purchase_price
        asset.current_value = current_value
        asset.warranty_expiry = parse_date(warranty_expiry_str)
        asset.supplier = supplier
        asset.condition = condition
        asset.description = description
        asset.notes = notes
        asset.updated_at = datetime.utcnow()

        db.session.commit()

        new_val_summary = f"Val: ${asset.current_value}, Cond: {asset.condition}"
        log_transaction(
            asset_id=asset.id,
            transaction_type='Information Updated',
            old_value=old_val_summary,
            new_value=new_val_summary,
            performed_by=current_user.email,
            notes='Asset details modified'
        )

        flash(f'Asset "{asset.name}" updated successfully.', 'success')
        return redirect(url_for('assets.details', asset_id=asset.id))

    return render_template('asset_form.html', action='edit', asset=asset, categories=categories, locations=locations, employees=employees)

@assets_bp.route('/<int:asset_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    name = asset.name
    code = asset.asset_code

    db.session.delete(asset)
    db.session.commit()

    flash(f'Asset "{name}" ({code}) has been permanently deleted.', 'info')
    return redirect(url_for('assets.index'))

@assets_bp.route('/<int:asset_id>/assign', methods=['POST'])
@login_required
@manager_or_admin_required
def assign(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    employee_id = request.form.get('employee_id', type=int)
    assigned_date_str = request.form.get('assigned_date', '').strip()
    notes = request.form.get('notes', '').strip()

    if not employee_id:
        flash('Please select an employee to assign this asset.', 'danger')
        return redirect(url_for('assets.details', asset_id=asset.id))

    employee = Employee.query.get_or_404(employee_id)
    assigned_date = parse_date(assigned_date_str) or date.today()

    # If already assigned to someone, close existing active assignment
    if asset.assigned_to:
        old_asgn = AssetAssignment.query.filter_by(asset_id=asset.id, assignment_status='Active').first()
        if old_asgn:
            old_asgn.returned_date = assigned_date
            old_asgn.assignment_status = 'Returned'

    # Create new assignment
    new_asgn = AssetAssignment(
        asset_id=asset.id,
        employee_id=employee.id,
        assigned_date=assigned_date,
        assignment_status='Active',
        notes=notes
    )
    db.session.add(new_asgn)

    old_status = asset.status
    asset.status = 'Assigned'
    asset.assigned_to = employee.id
    db.session.commit()

    log_transaction(
        asset_id=asset.id,
        transaction_type='Assignment',
        old_value=old_status,
        new_value=f'Assigned to {employee.name} ({employee.employee_code})',
        performed_by=current_user.email,
        notes=notes or 'Asset assigned to employee'
    )

    flash(f'Asset assigned to {employee.name} successfully.', 'success')
    return redirect(url_for('assets.details', asset_id=asset.id))

@assets_bp.route('/<int:asset_id>/return', methods=['POST'])
@login_required
@manager_or_admin_required
def return_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    notes = request.form.get('notes', '').strip()
    condition = request.form.get('condition', asset.condition)
    returned_date_str = request.form.get('returned_date', '').strip()
    returned_date = parse_date(returned_date_str) or date.today()

    emp_name = asset.assigned_employee.name if asset.assigned_employee else 'Unknown'

    # Close active assignment
    active_asgn = AssetAssignment.query.filter_by(asset_id=asset.id, assignment_status='Active').first()
    if active_asgn:
        active_asgn.returned_date = returned_date
        active_asgn.assignment_status = 'Returned'
        if notes:
            active_asgn.notes = (active_asgn.notes or '') + f' | Return Notes: {notes}'

    asset.status = 'Available'
    asset.assigned_to = None
    asset.condition = condition
    db.session.commit()

    log_transaction(
        asset_id=asset.id,
        transaction_type='Return',
        old_value=f'Assigned to {emp_name}',
        new_value='Available',
        performed_by=current_user.email,
        notes=f"Returned by {emp_name}. Condition: {condition}. {notes}"
    )

    flash(f'Asset returned successfully. Status is now Available.', 'success')
    return redirect(url_for('assets.details', asset_id=asset.id))

@assets_bp.route('/<int:asset_id>/status', methods=['POST'])
@login_required
@manager_or_admin_required
def change_status(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    new_status = request.form.get('status')
    notes = request.form.get('notes', '').strip()

    valid_statuses = ['Available', 'Assigned', 'Under Maintenance', 'Lost', 'Retired', 'Disposed']
    if new_status not in valid_statuses:
        flash('Invalid status selected.', 'danger')
        return redirect(url_for('assets.details', asset_id=asset.id))

    old_status = asset.status

    # If retiring or disposing or sending to maintenance, unassign if needed
    if new_status in ['Under Maintenance', 'Lost', 'Retired', 'Disposed'] and asset.assigned_to:
        active_asgn = AssetAssignment.query.filter_by(asset_id=asset.id, assignment_status='Active').first()
        if active_asgn:
            active_asgn.returned_date = date.today()
            active_asgn.assignment_status = 'Returned'
            active_asgn.notes = (active_asgn.notes or '') + f' | Unassigned due to status change to {new_status}'
        asset.assigned_to = None

    asset.status = new_status
    db.session.commit()

    log_transaction(
        asset_id=asset.id,
        transaction_type='Status Change',
        old_value=old_status,
        new_value=new_status,
        performed_by=current_user.email,
        notes=notes or f"Status changed from {old_status} to {new_status}"
    )

    flash(f'Asset status changed to {new_status}.', 'success')
    return redirect(url_for('assets.details', asset_id=asset.id))
