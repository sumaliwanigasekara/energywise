from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.appliances import UserAppliances

appliances_bp = Blueprint("appliances", __name__)

_FIELDS = [
    "fan_count", "fan_hours_per_month",
    "ac_count", "ac_hours_per_month", "ac_tons", "ac_units",
    "fridge_count", "washer_hours_per_month", "heater_hours_per_month",
    "other_hours_per_month",
]


def _aggregate_ac(ac_units: list) -> dict:
    """Compute ac_count, ac_hours_per_month (avg), ac_tons (hours-weighted avg)
    so that ac_count * ac_hours_per_month * ac_tons == sum(tons_i * hours_i_per_month).
    """
    units = [u for u in (ac_units or []) if u.get("hours_per_day", 0) > 0 or u.get("tons", 0) > 0]
    count = len(units)
    if count == 0:
        return {"ac_count": 0, "ac_hours_per_month": 0.0, "ac_tons": 1.5}

    total_hours = sum(u.get("hours_per_day", 0) * 30 for u in units)
    avg_hours   = total_hours / count
    sum_ton_hrs = sum(u.get("tons", 1.5) * u.get("hours_per_day", 0) * 30 for u in units)
    weighted_tons = (sum_ton_hrs / total_hours) if total_hours > 0 else (
        sum(u.get("tons", 1.5) for u in units) / count
    )
    return {
        "ac_count":          count,
        "ac_hours_per_month": round(avg_hours, 2),
        "ac_tons":            round(weighted_tons, 3),
    }


@appliances_bp.route("/appliances", methods=["GET", "POST", "PUT"])
@jwt_required()
def appliances():
    user_id = int(get_jwt_identity())

    if request.method == "GET":
        profile = UserAppliances.query.filter_by(user_id=user_id).first()
        if not profile:
            return jsonify({"message": "No appliance profile found"}), 404
        return jsonify(profile.to_dict()), 200

    data = request.get_json() or {}

    # If ac_units list provided, derive aggregated AC fields from it
    if "ac_units" in data and isinstance(data["ac_units"], list):
        data.update(_aggregate_ac(data["ac_units"]))

    if request.method == "POST":
        if UserAppliances.query.filter_by(user_id=user_id).first():
            return jsonify({"message": "Profile already exists, use PUT to update"}), 409

        profile = UserAppliances(user_id=user_id)
        for field in _FIELDS:
            if data.get(field) is not None:
                setattr(profile, field, data[field])

        db.session.add(profile)
        db.session.commit()
        return jsonify(profile.to_dict()), 201

    if request.method == "PUT":
        profile = UserAppliances.query.filter_by(user_id=user_id).first()
        if not profile:
            return jsonify({"message": "No appliance profile found, use POST to create"}), 404

        for field in _FIELDS:
            if data.get(field) is not None:
                setattr(profile, field, data[field])

        profile.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return jsonify(profile.to_dict()), 200
