from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.weather_service import get_weather

weather_bp = Blueprint("weather", __name__)


@weather_bp.route("/weather", methods=["GET"])
@jwt_required()
def weather():
    district = request.args.get("district", "colombo")
    data = get_weather(district)
    return jsonify(data), 200
