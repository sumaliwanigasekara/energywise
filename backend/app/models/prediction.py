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
    predicted_bill = db.Column(db.Float)
    risk_level = db.Column(db.String(20))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "members": self.members,
            "district": self.district,
            "prev_bills": [self.prev_bill_1, self.prev_bill_2, self.prev_bill_3],
            "appliances": {
                "fan_count": self.fan_count,
                "ac_count": self.ac_count,
                "ac_hours_per_month": self.ac_hours_per_month,
                "ac_tons": self.ac_tons,
                "fridge_count": self.fridge_count,
                "washer_hours_per_month": self.washer_hours_per_month,
                "heater_hours_per_month": self.heater_hours_per_month,
                "other_hours_per_month": self.other_hours_per_month,
            },
            "weather": {
                "avg_temp": self.avg_temp,
                "avg_humidity": self.avg_humidity,
                "total_precip": self.total_precip,
                "avg_wind": self.avg_wind,
                "period": (
                    f"{self.start_date.date()} to {self.end_date.date()}"
                    if self.start_date and self.end_date else None
                )
            },
            "prediction": {
                "units": round(self.predicted_units, 2),
                "bill": round(self.predicted_bill, 2),
                "risk_level": self.risk_level,
            },
            "created_at": self.created_at.isoformat(),
        }
