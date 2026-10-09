from datetime import datetime
from utils.database import db

class Asset(db.Model):
    __tablename__ = 'assets'

    id = db.Column(db.Integer, primary_key=True)
    asset_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    description = db.Column(db.Text, nullable=True)
    manufacturer = db.Column(db.String(100), nullable=True)
    model = db.Column(db.String(100), nullable=True)
    serial_number = db.Column(db.String(100), unique=True, nullable=True, index=True)
    purchase_date = db.Column(db.Date, nullable=True)
    purchase_price = db.Column(db.Float, default=0.0)
    current_value = db.Column(db.Float, default=0.0)
    warranty_expiry = db.Column(db.Date, nullable=True)
    supplier = db.Column(db.String(100), nullable=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=True)
    status = db.Column(db.String(30), default='Available')  # Available, Assigned, Under Maintenance, Lost, Retired, Disposed
    condition = db.Column(db.String(30), default='Good')  # Excellent, Good, Fair, Poor, Damaged
    assigned_to = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    image = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category = db.relationship('Category', back_populates='assets')
    location = db.relationship('Location', back_populates='assets')
    assigned_employee = db.relationship('Employee', foreign_keys=[assigned_to], back_populates='assigned_assets')
    
    assignments = db.relationship('AssetAssignment', back_populates='asset', lazy='dynamic', cascade='all, delete-orphan', order_by='desc(AssetAssignment.id)')
    maintenance_records = db.relationship('MaintenanceRecord', back_populates='asset', lazy='dynamic', cascade='all, delete-orphan', order_by='desc(MaintenanceRecord.id)')
    transactions = db.relationship('AssetTransaction', back_populates='asset', lazy='dynamic', cascade='all, delete-orphan', order_by='desc(AssetTransaction.id)')

    @property
    def status_badge_class(self):
        badges = {
            'Available': 'badge bg-success',
            'Assigned': 'badge bg-primary',
            'Under Maintenance': 'badge bg-warning text-dark',
            'Lost': 'badge bg-danger',
            'Retired': 'badge bg-secondary',
            'Disposed': 'badge bg-dark'
        }
        return badges.get(self.status, 'badge bg-secondary')

    @property
    def condition_badge_class(self):
        badges = {
            'Excellent': 'badge bg-success',
            'Good': 'badge bg-info text-dark',
            'Fair': 'badge bg-warning text-dark',
            'Poor': 'badge bg-orange text-dark',
            'Damaged': 'badge bg-danger'
        }
        return badges.get(self.condition, 'badge bg-secondary')

    @property
    def total_maintenance_cost(self):
        return sum([m.cost for m in self.maintenance_records.all() if m.cost])

    def to_dict(self):
        return {
            'id': self.id,
            'asset_code': self.asset_code,
            'name': self.name,
            'category': self.category.name if self.category else 'Uncategorized',
            'category_id': self.category_id,
            'manufacturer': self.manufacturer or '',
            'model': self.model or '',
            'serial_number': self.serial_number or '',
            'purchase_date': self.purchase_date.strftime('%Y-%m-%d') if self.purchase_date else '',
            'purchase_price': round(self.purchase_price or 0.0, 2),
            'current_value': round(self.current_value or 0.0, 2),
            'warranty_expiry': self.warranty_expiry.strftime('%Y-%m-%d') if self.warranty_expiry else '',
            'supplier': self.supplier or '',
            'location': self.location.name if self.location else 'Not Specified',
            'location_id': self.location_id,
            'status': self.status,
            'condition': self.condition,
            'assigned_to': self.assigned_employee.name if self.assigned_employee else None,
            'assigned_to_id': self.assigned_to,
            'image': self.image or '',
            'notes': self.notes or '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else '',
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else ''
        }

    def __repr__(self):
        return f'<Asset {self.asset_code} - {self.name}>'

