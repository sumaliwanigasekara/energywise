from app.extensions import db
from datetime import datetime


class Prediction(db.Model):
    __tablename__ = "predictions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Household inputs
    members = db.Column(db.Integer)
    district = db.Column(db.String(100))

    # Previous bills
    prev_bill_1 = db.Column(db.Float)
    prev_bill_2 = db.Column(db.Float)
    prev_bill_3 = db.Column(db.Float)

    # Appliances — monthly hour totals
    fan_count = db.Column(db.Integer)
    ac_count = db.Column(db.Integer)
    ac_hours_per_month = db.Column(db.Float)
    ac_tons = db.Column(db.Float)
    fridge_count = db.Column(db.Integer)
    washer_hours_per_month = db.Column(db.Float)
    heater_hours_per_month = db.Column(db.Float)
    other_hours_per_month = db.Column(db.Float)

    # Weather — 30-day monthly averages (ML features)
    avg_temp = db.Column(db.Float)
    avg_humidity = db.Column(db.Float)
    total_precip = db.Column(db.Float)
    avg_wind = db.Column(db.Float)

    # Temporal
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)

    # ML outputs
    predicted_units = db.Column(db.Float)
    predicted_bill  = db.Column(db.Float)
    risk_level      = db.Column(db.String(20))
    recommendations     = db.Column(db.JSON, nullable=True)
    appliance_breakdown = db.Column(db.JSON, nullable=True)

    # Actual bill entered by consumer after month ends
    actual_units = db.Column(db.Float, nullable=True)
    actual_bill  = db.Column(db.Float, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "members": self.members,
            "district": self.district,
            "predicted_units": round(self.predicted_units, 2) if self.predicted_units else 0,
            "predicted_bill":  round(self.predicted_bill,  2) if self.predicted_bill  else 0,
            "risk_level": self.risk_level,
            "avg_temp":    self.avg_temp,
            "avg_humidity": self.avg_humidity,
            "total_precip": self.total_precip,
            "avg_wind":     self.avg_wind,
            "prev_bill_1": self.prev_bill_1,
            "prev_bill_2": self.prev_bill_2,
            "prev_bill_3": self.prev_bill_3,
            "recommendations":     self.recommendations    or [],
            "appliance_breakdown": self.appliance_breakdown or {},
            "actual_units": self.actual_units,
            "actual_bill":  self.actual_bill,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
