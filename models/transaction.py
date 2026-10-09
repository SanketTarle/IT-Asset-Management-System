from datetime import datetime
from utils.database import db

class AssetTransaction(db.Model):
    __tablename__ = 'asset_transactions'

    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)  # Registration, Assignment, Return, Maintenance, Update, Disposal, Status Change
    old_value = db.Column(db.Text, nullable=True)
    new_value = db.Column(db.Text, nullable=True)
    performed_by = db.Column(db.String(100), nullable=True)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)

    # Relationships
    asset = db.relationship('Asset', back_populates='transactions')

    def to_dict(self):
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'asset_code': self.asset.asset_code if self.asset else '',
            'transaction_type': self.transaction_type,
            'old_value': self.old_value or '',
            'new_value': self.new_value or '',
            'performed_by': self.performed_by or 'System',
            'transaction_date': self.transaction_date.strftime('%Y-%m-%d %H:%M:%S') if self.transaction_date else '',
            'notes': self.notes or ''
        }

    def __repr__(self):
        return f'<AssetTransaction Asset:{self.asset_id} - {self.transaction_type}>'

