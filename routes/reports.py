import csv
import io
from datetime import datetime
from flask import Blueprint, render_template, request, make_response, flash, redirect, url_for
from flask_login import login_required
from sqlalchemy import func
from utils.database import db
from models.asset import Asset
from models.category import Category
from models.location import Location
from models.employee import Employee
from models.maintenance import MaintenanceRecord
from models.assignment import AssetAssignment

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
@login_required
def index():
    report_type = request.args.get('type', 'all_assets')
    category_id = request.args.get('category_id', type=int)
    location_id = request.args.get('location_id', type=int)
    
    categories = Category.query.order_by(Category.name).all()
    locations = Location.query.order_by(Location.name).all()

    data = []
    summary = {}

    if report_type == 'all_assets':
        q = Asset.query
        if category_id:
            q = q.filter_by(category_id=category_id)
        if location_id:
            q = q.filter_by(location_id=location_id)
        data = q.order_by(Asset.asset_code).all()
        summary = {
            'count': len(data),
            'total_purchase': sum([a.purchase_price or 0.0 for a in data]),
            'total_current': sum([a.current_value or 0.0 for a in data])
        }

    elif report_type == 'assigned_assets':
        q = Asset.query.filter_by(status='Assigned')
        if category_id:
            q = q.filter_by(category_id=category_id)
        if location_id:
            q = q.filter_by(location_id=location_id)
        data = q.order_by(Asset.asset_code).all()
        summary = {
            'count': len(data),
            'total_value': sum([a.current_value or 0.0 for a in data])
        }

    elif report_type == 'available_assets':
        q = Asset.query.filter_by(status='Available')
        if category_id:
            q = q.filter_by(category_id=category_id)
        if location_id:
            q = q.filter_by(location_id=location_id)
        data = q.order_by(Asset.asset_code).all()
        summary = {
            'count': len(data),
            'total_value': sum([a.current_value or 0.0 for a in data])
        }

    elif report_type == 'maintenance':
        q = MaintenanceRecord.query
        data = q.order_by(MaintenanceRecord.maintenance_date.desc()).all()
        summary = {
            'count': len(data),
            'total_cost': sum([m.cost or 0.0 for m in data])
        }

    elif report_type == 'retired_assets':
        data = Asset.query.filter(Asset.status.in_(['Retired', 'Disposed'])).order_by(Asset.asset_code).all()
        summary = {
            'count': len(data),
            'total_salvage': sum([a.current_value or 0.0 for a in data])
        }

    elif report_type == 'asset_value':
        data = Asset.query.order_by(Asset.current_value.desc()).all()
        summary = {
            'count': len(data),
            'total_purchase': sum([a.purchase_price or 0.0 for a in data]),
            'total_current': sum([a.current_value or 0.0 for a in data]),
            'total_depreciation': sum([(a.purchase_price or 0.0) - (a.current_value or 0.0) for a in data])
        }

    elif report_type == 'employee_assets':
        data = Employee.query.filter_by(status='Active').order_by(Employee.name).all()
        summary = {
            'total_employees': len(data),
            'employees_with_assets': sum([1 for e in data if e.assigned_assets.count() > 0])
        }

    return render_template(
        'reports.html',
        report_type=report_type,
        data=data,
        summary=summary,
        categories=categories,
        locations=locations,
        category_id=category_id,
        location_id=location_id
    )

@reports_bp.route('/export-csv')
@login_required
def export_csv():
    report_type = request.args.get('type', 'all_assets')
    output = io.StringIO()
    writer = csv.writer(output)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{report_type}_report_{timestamp}.csv"

    if report_type in ['all_assets', 'assigned_assets', 'available_assets', 'retired_assets', 'asset_value']:
        q = Asset.query
        if report_type == 'assigned_assets':
            q = q.filter_by(status='Assigned')
        elif report_type == 'available_assets':
            q = q.filter_by(status='Available')
        elif report_type == 'retired_assets':
            q = q.filter(Asset.status.in_(['Retired', 'Disposed']))
        
        assets = q.order_by(Asset.asset_code).all()

        writer.writerow([
            'Asset Code', 'Asset Name', 'Category', 'Manufacturer', 'Model',
            'Serial Number', 'Status', 'Condition', 'Location', 'Assigned To',
            'Purchase Date', 'Purchase Price ($)', 'Current Value ($)', 'Warranty Expiry', 'Supplier'
        ])

        for a in assets:
            writer.writerow([
                a.asset_code,
                a.name,
                a.category.name if a.category else '',
                a.manufacturer or '',
                a.model or '',
                a.serial_number or '',
                a.status,
                a.condition,
                a.location.name if a.location else '',
                a.assigned_employee.name if a.assigned_employee else 'Unassigned',
                a.purchase_date.strftime('%Y-%m-%d') if a.purchase_date else '',
                f"{a.purchase_price:.2f}" if a.purchase_price else '0.00',
                f"{a.current_value:.2f}" if a.current_value else '0.00',
                a.warranty_expiry.strftime('%Y-%m-%d') if a.warranty_expiry else '',
                a.supplier or ''
            ])

    elif report_type == 'maintenance':
        records = MaintenanceRecord.query.order_by(MaintenanceRecord.maintenance_date.desc()).all()
        writer.writerow([
            'Record ID', 'Asset Code', 'Asset Name', 'Maintenance Type',
            'Description', 'Maintenance Date', 'Cost ($)', 'Service Provider',
            'Next Service Date', 'Status'
        ])
        for r in records:
            writer.writerow([
                r.id,
                r.asset.asset_code if r.asset else '',
                r.asset.name if r.asset else '',
                r.maintenance_type,
                r.description,
                r.maintenance_date.strftime('%Y-%m-%d') if r.maintenance_date else '',
                f"{r.cost:.2f}" if r.cost else '0.00',
                r.service_provider or '',
                r.next_service_date.strftime('%Y-%m-%d') if r.next_service_date else '',
                r.status
            ])

    elif report_type == 'employee_assets':
        employees = Employee.query.order_by(Employee.name).all()
        writer.writerow([
            'Employee Code', 'Name', 'Email', 'Department', 'Designation',
            'Location', 'Status', 'Assigned Assets Count', 'Assigned Assets List'
        ])
        for e in employees:
            asset_list = "; ".join([f"{a.asset_code} ({a.name})" for a in e.assigned_assets])
            writer.writerow([
                e.employee_code,
                e.name,
                e.email,
                e.department or '',
                e.designation or '',
                e.location.name if e.location else '',
                e.status,
                e.assigned_assets.count(),
                asset_list
            ])

    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    response.headers['Content-type'] = 'text/csv; charset=utf-8'
    return response

