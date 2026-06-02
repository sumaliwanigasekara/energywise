from app.extensions import db
from datetime import datetime


class UserAppliances(db.Model):
    __tablename__ = "user_appliances"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)

    fan_count = db.Column(db.Integer, default=0)
    ac_count = db.Column(db.Integer, default=0)
    ac_hours_per_month = db.Column(db.Float, default=0)
    ac_tons = db.Column(db.Float, default=1.5)
    fridge_count = db.Column(db.Integer, default=1)
    washer_hours_per_month = db.Column(db.Float, default=0)
    heater_hours_per_month = db.Column(db.Float, default=0)
    other_hours_per_month = db.Column(db.Float, default=0)

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "fan_count": self.fan_count,
            "ac_count": self.ac_count,
            "ac_hours_per_month": self.ac_hours_per_month,
            "ac_tons": self.ac_tons,
            "fridge_count": self.fridge_count,
            "washer_hours_per_month": self.washer_hours_per_month,
            "heater_hours_per_month": self.heater_hours_per_month,
            "other_hours_per_month": self.other_hours_per_month,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
