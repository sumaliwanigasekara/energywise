from app.extensions import db
from datetime import datetime, timezone

def _now():
    return datetime.now(timezone.utc)


class UserAppliances(db.Model):
    __tablename__ = "user_appliances"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)

    fan_count = db.Column(db.Integer, default=0)
    fan_hours_per_month = db.Column(db.Float, default=0)

    # Aggregated AC fields (computed from ac_units, kept for ML compatibility)
    ac_count = db.Column(db.Integer, default=0)
    ac_hours_per_month = db.Column(db.Float, default=0)
    ac_tons = db.Column(db.Float, default=1.5)
    # Individual AC configurations: [{"tons": 1.5, "hours_per_day": 6}, ...]
    ac_units = db.Column(db.JSON, nullable=True)

    fridge_count = db.Column(db.Integer, default=1)
    washer_hours_per_month = db.Column(db.Float, default=0)
    heater_hours_per_month = db.Column(db.Float, default=0)
    other_hours_per_month = db.Column(db.Float, default=0)

    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "fan_count": self.fan_count,
            "fan_hours_per_month": self.fan_hours_per_month,
            "ac_count": self.ac_count,
            "ac_hours_per_month": self.ac_hours_per_month,
            "ac_tons": self.ac_tons,
            "ac_units": self.ac_units or [],
            "fridge_count": self.fridge_count,
            "washer_hours_per_month": self.washer_hours_per_month,
            "heater_hours_per_month": self.heater_hours_per_month,
            "other_hours_per_month": self.other_hours_per_month,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
