from datetime import datetime
from utils.database import db

class Employee(db.Model):
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    employee_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(30), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    designation = db.Column(db.String(100), nullable=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=True)
    status = db.Column(db.String(20), default='Active')  # Active, Inactive, On Leave, Terminated
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    location = db.relationship('Location', back_populates='employees')
    assignments = db.relationship('AssetAssignment', back_populates='employee', lazy='dynamic', cascade='all, delete-orphan')
    assigned_assets = db.relationship('Asset', back_populates='assigned_employee', lazy='dynamic')

    @property
    def active_assigned_count(self):
        return self.assigned_assets.count()

    def to_dict(self):
        return {
            'id': self.id,
            'employee_code': self.employee_code,
            'name': self.name,
            'email': self.email,
            'phone': self.phone or '',
            'department': self.department or '',
            'designation': self.designation or '',
            'location': self.location.name if self.location else 'Not Specified',
            'location_id': self.location_id,
            'status': self.status,
            'assigned_assets_count': self.active_assigned_count,
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else ''
        }

    def __repr__(self):
        return f'<Employee {self.employee_code} - {self.name}>'

