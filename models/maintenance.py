from datetime import datetime, date
from utils.database import db

class MaintenanceRecord(db.Model):
    __tablename__ = 'maintenance_records'

    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    maintenance_type = db.Column(db.String(50), nullable=False)  # Repair, Inspection, Routine, Upgrade, Calibration, Other
    description = db.Column(db.Text, nullable=False)
    maintenance_date = db.Column(db.Date, nullable=False, default=date.today)
    cost = db.Column(db.Float, default=0.0)
    service_provider = db.Column(db.String(100), nullable=True)
    next_service_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(30), default='Scheduled')  # Scheduled, In Progress, Completed, Cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    asset = db.relationship('Asset', back_populates='maintenance_records')

    @property
    def status_badge_class(self):
        badges = {
            'Scheduled': 'badge bg-info text-dark',
            'In Progress': 'badge bg-warning text-dark',
            'Completed': 'badge bg-success',
            'Cancelled': 'badge bg-secondary'
        }
        return badges.get(self.status, 'badge bg-secondary')

    def to_dict(self):
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'asset_code': self.asset.asset_code if self.asset else '',
            'asset_name': self.asset.name if self.asset else '',
            'maintenance_type': self.maintenance_type,
            'description': self.description,
            'maintenance_date': self.maintenance_date.strftime('%Y-%m-%d') if self.maintenance_date else '',
            'cost': round(self.cost or 0.0, 2),
            'service_provider': self.service_provider or '',
            'next_service_date': self.next_service_date.strftime('%Y-%m-%d') if self.next_service_date else '',
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }

    def __repr__(self):
        return f'<MaintenanceRecord Asset:{self.asset_id} - {self.maintenance_type}>'

