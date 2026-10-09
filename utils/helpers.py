import os
import uuid
from datetime import datetime, date
from werkzeug.utils import secure_filename
from flask import current_app
from utils.database import db
from models.transaction import AssetTransaction
from models.asset import Asset
from models.employee import Employee

def allowed_file(filename):
    """Check if uploaded file has an allowed extension."""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config['ALLOWED_EXTENSIONS']

def save_asset_image(file):
    """
    Save uploaded asset image to static/uploads/assets/
    Returns filename if successful, None otherwise.
    """
    if not file or file.filename == '':
        return None
    
    if not allowed_file(file.filename):
        return None
    
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    
    original_ext = secure_filename(file.filename).rsplit('.', 1)[1].lower()
    unique_filename = f"asset_{uuid.uuid4().hex[:12]}.{original_ext}"
    filepath = os.path.join(upload_folder, unique_filename)
    file.save(filepath)
    return unique_filename

def generate_asset_code():
    """
    Generate unique asset code in format AST-00001.
    Finds the highest existing code number and increments by 1.
    """
    highest = 0
    assets = Asset.query.all()
    for a in assets:
        if a.asset_code and a.asset_code.startswith('AST-'):
            try:
                num = int(a.asset_code.split('-')[1])
                if num > highest:
                    highest = num
            except (IndexError, ValueError):
                pass
    next_num = highest + 1
    return f"AST-{next_num:05d}"

def generate_employee_code():
    """
    Generate unique employee code in format EMP-0001.
    """
    highest = 0
    employees = Employee.query.all()
    for emp in employees:
        if emp.employee_code and emp.employee_code.startswith('EMP-'):
            try:
                num = int(emp.employee_code.split('-')[1])
                if num > highest:
                    highest = num
            except (IndexError, ValueError):
                pass
    next_num = highest + 1
    return f"EMP-{next_num:04d}"

def log_transaction(asset_id, transaction_type, old_value=None, new_value=None, performed_by=None, notes=None):
    """
    Helper function to log audit transactions for any asset operation.
    """
    try:
        tx = AssetTransaction(
            asset_id=asset_id,
            transaction_type=transaction_type,
            old_value=str(old_value) if old_value is not None else None,
            new_value=str(new_value) if new_value is not None else None,
            performed_by=performed_by or 'System',
            notes=notes
        )
        db.session.add(tx)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error logging asset transaction: {e}")

def parse_date(date_str):
    """Safely parse YYYY-MM-DD date string to date object."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str.strip(), '%Y-%m-%d').date()
    except (ValueError, AttributeError):
        return None

def format_currency(val):
    """Format float into USD currency representation."""
    try:
        return f"${float(val):,.2f}"
    except (TypeError, ValueError):
        return "$0.00"

