from datetime import datetime
from utils.database import db

class Location(db.Model):
    __tablename__ = 'locations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    building = db.Column(db.String(100), nullable=True)
    floor = db.Column(db.String(50), nullable=True)
    room = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    assets = db.relationship('Asset', back_populates='location', lazy='dynamic')
    employees = db.relationship('Employee', back_populates='location', lazy='dynamic')

    @property
    def full_location(self):
        parts = [self.name]
        if self.building:
            parts.append(f"Bldg: {self.building}")
        if self.floor:
            parts.append(f"Flr: {self.floor}")
        if self.room:
            parts.append(f"Rm: {self.room}")
        return " - ".join(parts)

    @property
    def asset_count(self):
        return self.assets.count()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'building': self.building or '',
            'floor': self.floor or '',
            'room': self.room or '',
            'description': self.description or '',
            'full_location': self.full_location,
            'asset_count': self.asset_count,
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else ''
        }

    def __repr__(self):
        return f'<Location {self.name}>'

