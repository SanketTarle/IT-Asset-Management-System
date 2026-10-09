from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from utils.database import db
from utils.decorators import admin_required, manager_or_admin_required
from utils.helpers import parse_date, log_transaction
from models.maintenance import MaintenanceRecord
from models.asset import Asset

maintenance_bp = Blueprint('maintenance', __name__, url_prefix='/maintenance')

@maintenance_bp.route('/')
@login_required
def index():
    status = request.args.get('status', '').strip()
    query = MaintenanceRecord.query

    if status:
        query = query.filter(MaintenanceRecord.status == status)

    records = query.order_by(MaintenanceRecord.maintenance_date.desc(), MaintenanceRecord.id.desc()).all()
    # Assets eligible for maintenance (exclude retired/disposed)
    assets = Asset.query.filter(~Asset.status.in_(['Retired', 'Disposed'])).order_by(Asset.name).all()

    total_cost = sum([r.cost for r in records if r.cost])
    in_progress_count = MaintenanceRecord.query.filter_by(status='In Progress').count()
    scheduled_count = MaintenanceRecord.query.filter_by(status='Scheduled').count()

    return render_template(
        'maintenance.html',
        records=records,
        assets=assets,
        selected_status=status,
        total_cost=total_cost,
        in_progress_count=in_progress_count,
        scheduled_count=scheduled_count
    )

@maintenance_bp.route('/add', methods=['POST'])
@login_required
@manager_or_admin_required
def add():
    asset_id = request.form.get('asset_id', type=int)
    maintenance_type = request.form.get('maintenance_type', '').strip()
    description = request.form.get('description', '').strip()
    maintenance_date_str = request.form.get('maintenance_date', '').strip()
    service_provider = request.form.get('service_provider', '').strip()
    next_service_date_str = request.form.get('next_service_date', '').strip()
    status = request.form.get('status', 'Scheduled')

    try:
        cost = float(request.form.get('cost') or 0.0)
    except ValueError:
        cost = 0.0

    if not asset_id or not maintenance_type or not description:
        flash('Asset, maintenance type, and description are required.', 'danger')
        return redirect(url_for('maintenance.index'))

    asset = Asset.query.get_or_404(asset_id)
    maint_date = parse_date(maintenance_date_str) or date.today()
    next_date = parse_date(next_service_date_str)

    record = MaintenanceRecord(
        asset_id=asset.id,
        maintenance_type=maintenance_type,
        description=description,
        maintenance_date=maint_date,
        cost=cost,
        service_provider=service_provider,
        next_service_date=next_date,
        status=status
    )
    db.session.add(record)

    # When maintenance is scheduled or in progress, asset status automatically becomes Under Maintenance
    if status in ['Scheduled', 'In Progress']:
        old_status = asset.status
        asset.status = 'Under Maintenance'
        log_transaction(
            asset_id=asset.id,
            transaction_type='Maintenance Scheduled',
            old_value=old_status,
            new_value='Under Maintenance',
            performed_by=current_user.email,
            notes=f"Maintenance ({maintenance_type}) by {service_provider or 'internal team'}"
        )

    db.session.commit()
    flash('Maintenance record created successfully.', 'success')
    return redirect(url_for('maintenance.index'))

@maintenance_bp.route('/<int:record_id>/edit', methods=['POST'])
@login_required
@manager_or_admin_required
def edit(record_id):
    record = MaintenanceRecord.query.get_or_404(record_id)
    
    record.maintenance_type = request.form.get('maintenance_type', record.maintenance_type).strip()
    record.description = request.form.get('description', record.description).strip()
    record.service_provider = request.form.get('service_provider', record.service_provider).strip()
    record.status = request.form.get('status', record.status)
    
    maint_date_str = request.form.get('maintenance_date', '').strip()
    if maint_date_str:
        record.maintenance_date = parse_date(maint_date_str)

    next_date_str = request.form.get('next_service_date', '').strip()
    record.next_service_date = parse_date(next_date_str)

    try:
        record.cost = float(request.form.get('cost') or 0.0)
    except ValueError:
        pass

    # If status marked Completed and asset is Under Maintenance, restore to Available
    if record.status == 'Completed' and record.asset.status == 'Under Maintenance':
        record.asset.status = 'Available'
        log_transaction(
            asset_id=record.asset.id,
            transaction_type='Maintenance Completed',
            old_value='Under Maintenance',
            new_value='Available',
            performed_by=current_user.email,
            notes=f"Completed {record.maintenance_type}. Cost: ${record.cost:.2f}"
        )

    db.session.commit()
    flash('Maintenance record updated successfully.', 'success')
    return redirect(url_for('maintenance.index'))

@maintenance_bp.route('/<int:record_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(record_id):
    record = MaintenanceRecord.query.get_or_404(record_id)
    db.session.delete(record)
    db.session.commit()

    flash('Maintenance record deleted successfully.', 'info')
    return redirect(url_for('maintenance.index'))

