from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.prediction import Prediction
from app.models.appliances import UserAppliances
from app.services import ml_service
from app.services.weather_service import get_weather

predict_bp = Blueprint("predict", __name__)


@predict_bp.route("/predict", methods=["POST"])
@jwt_required()
def predict():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    # Fall back to saved appliance profile for fields not supplied in the request
    profile = UserAppliances.query.filter_by(user_id=user_id).first()

    def _from_profile(key, default):
        if data.get(key) is not None:
            return data[key]
        return getattr(profile, key, default) if profile else default

    district = data.get("district") or _from_profile("district", "colombo")
    weather = get_weather(district)

    def _parse_date(val):
        if val is None:
            return None
        try:
            return datetime.fromisoformat(val)
        except (ValueError, TypeError):
            return None

    payload = {
        "members": int(_from_profile("members", 4)),
        "prev_bill_1": float(data.get("prev_bill_1") or 0),
        "prev_bill_2": float(data.get("prev_bill_2") or 0),
        "prev_bill_3": float(data.get("prev_bill_3") or 0),
        "fan_count": int(_from_profile("fan_count", 0)),
        "ac_count": int(_from_profile("ac_count", 0)),
        "ac_hours_per_week": float(data.get("ac_hours_per_week") or 0),
        "ac_tons": float(_from_profile("ac_tons", 1.5)),
        "fridge_count": int(_from_profile("fridge_count", 1)),
        "washer_hours_per_week": float(data.get("washer_hours_per_week") or 0),
        "heater_hours_per_week": float(data.get("heater_hours_per_week") or 0),
        "other_hours_per_week": float(data.get("other_hours_per_week") or 2),
        "weather": weather,
    }

    result = ml_service.predict(payload)

    prediction = Prediction(
        user_id=user_id,
        district=district,
        members=payload["members"],
        prev_bill_1=payload["prev_bill_1"],
        prev_bill_2=payload["prev_bill_2"],
        prev_bill_3=payload["prev_bill_3"],
        fan_count=payload["fan_count"],
        ac_count=payload["ac_count"],
        ac_hours_per_week=payload["ac_hours_per_week"],
        ac_tons=payload["ac_tons"],
        fridge_count=payload["fridge_count"],
        washer_hours_per_week=payload["washer_hours_per_week"],
        heater_hours_per_week=payload["heater_hours_per_week"],
        other_hours_per_week=payload["other_hours_per_week"],
        avg_temp=weather.get("avg_temp"),
        avg_humidity=weather.get("avg_humidity"),
        total_precip=weather.get("total_precip"),
        avg_wind=weather.get("avg_wind"),
        start_date=_parse_date(weather.get("period_start")),
        end_date=_parse_date(weather.get("period_end")),
        predicted_units=result["predicted_units"],
        predicted_bill=result["predicted_bill"],
        risk_level=result["risk_level"],
    )
    db.session.add(prediction)
    db.session.commit()

    return jsonify({
        "prediction_id": prediction.id,
        "predicted_units": result["predicted_units"],
        "predicted_bill": result["predicted_bill"],
        "risk_level": result["risk_level"],
        "recommendations": result["recommendations"],
        "appliance_breakdown": result["appliance_breakdown"],
        "weather": weather,
    }), 200
