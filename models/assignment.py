from datetime import datetime, date
from utils.database import db

class AssetAssignment(db.Model):
    __tablename__ = 'asset_assignments'

    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    assigned_date = db.Column(db.Date, nullable=False, default=date.today)
    returned_date = db.Column(db.Date, nullable=True)
    assignment_status = db.Column(db.String(20), default='Active')  # Active, Returned
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    asset = db.relationship('Asset', back_populates='assignments')
    employee = db.relationship('Employee', back_populates='assignments')

    def to_dict(self):
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'asset_code': self.asset.asset_code if self.asset else '',
            'asset_name': self.asset.name if self.asset else '',
            'employee_id': self.employee_id,
            'employee_code': self.employee.employee_code if self.employee else '',
            'employee_name': self.employee.name if self.employee else '',
            'assigned_date': self.assigned_date.strftime('%Y-%m-%d') if self.assigned_date else '',
            'returned_date': self.returned_date.strftime('%Y-%m-%d') if self.returned_date else '',
            'assignment_status': self.assignment_status,
            'notes': self.notes or '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }

    def __repr__(self):
        return f'<AssetAssignment Asset:{self.asset_id} -> Emp:{self.employee_id}>'

