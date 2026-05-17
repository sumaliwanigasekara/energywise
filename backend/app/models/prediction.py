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

    # Appliances
    fan_count = db.Column(db.Integer)
    ac_count = db.Column(db.Integer)
    ac_hours_per_day = db.Column(db.Float)
    ac_tons = db.Column(db.Float)
    fridge_count = db.Column(db.Integer)
    washer_hours_per_week = db.Column(db.Float)
    heater_hours_per_week = db.Column(db.Float)
    other_hours_per_day = db.Column(db.Float)

    # Weather
    temperature = db.Column(db.Float)
    weather_condition = db.Column(db.String(100))

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
            "prev_bill_1": self.prev_bill_1,
            "prev_bill_2": self.prev_bill_2,
            "prev_bill_3": self.prev_bill_3,
            "fan_count": self.fan_count,
            "ac_count": self.ac_count,
            "ac_hours_per_day": self.ac_hours_per_day,
            "ac_tons": self.ac_tons,
            "fridge_count": self.fridge_count,
            "washer_hours_per_week": self.washer_hours_per_week,
            "heater_hours_per_week": self.heater_hours_per_week,
            "other_hours_per_day": self.other_hours_per_day,
            "temperature": self.temperature,
            "weather_condition": self.weather_condition,
            "predicted_units": round(self.predicted_units, 2),
            "predicted_bill": round(self.predicted_bill, 2),
            "risk_level": self.risk_level,
            "created_at": self.created_at.isoformat(),
        }
