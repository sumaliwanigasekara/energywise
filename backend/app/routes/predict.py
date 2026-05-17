from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.prediction import Prediction
from app.services import ml_service
from app.services.weather_service import get_weather

predict_bp = Blueprint("predict", __name__)


@predict_bp.route("/predict", methods=["POST"])
@jwt_required()
def predict():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    district = data.get("district", "colombo")
    weather = get_weather(district)

    temperature = data.get("temperature") or weather["temperature"]

    payload = {
        "members": int(data.get("members", 4)),
        "prev_bill_1": float(data.get("prev_bill_1") or 0),
        "prev_bill_2": float(data.get("prev_bill_2") or 0),
        "prev_bill_3": float(data.get("prev_bill_3") or 0),
        "fan_count": int(data.get("fan_count", 0)),
        "ac_count": int(data.get("ac_count", 0)),
        "ac_hours_per_day": float(data.get("ac_hours_per_day") or 0),
        "ac_tons": float(data.get("ac_tons") or 1.5),
        "fridge_count": int(data.get("fridge_count", 0)),
        "washer_hours_per_week": float(data.get("washer_hours_per_week") or 0),
        "heater_hours_per_week": float(data.get("heater_hours_per_week") or 0),
        "other_hours_per_day": float(data.get("other_hours_per_day") or 2),
        "temperature": float(temperature),
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
        ac_hours_per_day=payload["ac_hours_per_day"],
        ac_tons=payload["ac_tons"],
        fridge_count=payload["fridge_count"],
        washer_hours_per_week=payload["washer_hours_per_week"],
        heater_hours_per_week=payload["heater_hours_per_week"],
        other_hours_per_day=payload["other_hours_per_day"],
        temperature=payload["temperature"],
        weather_condition=weather.get("condition", ""),
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
