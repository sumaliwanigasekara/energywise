from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.appliances import UserAppliances

appliances_bp = Blueprint("appliances", __name__)

_FIELDS = [
    "fan_count", "fan_hours_per_month",
    "ac_count", "ac_hours_per_month", "ac_tons",
    "fridge_count", "washer_hours_per_month", "heater_hours_per_month",
    "other_hours_per_month",
]


@appliances_bp.route("/appliances", methods=["GET", "POST", "PUT"])
@jwt_required()
def appliances():
    user_id = int(get_jwt_identity())

    # GET — return existing profile
    if request.method == "GET":
        profile = UserAppliances.query.filter_by(user_id=user_id).first()
        if not profile:
            return jsonify({"message": "No appliance profile found"}), 404
        return jsonify(profile.to_dict()), 200

    # POST — create new profile
    if request.method == "POST":
        data = request.get_json() or {}

        if UserAppliances.query.filter_by(user_id=user_id).first():
            return jsonify({"message": "Profile already exists, use PUT to update"}), 409

        if not any(data.get(f) is not None for f in _FIELDS):
            return jsonify({"message": "At least one field must be provided"}), 400

        profile = UserAppliances(user_id=user_id)
        for field in _FIELDS:
            if data.get(field) is not None:
                setattr(profile, field, data[field])

        db.session.add(profile)
        db.session.commit()
        return jsonify(profile.to_dict()), 201

    # PUT — update existing profile
    if request.method == "PUT":
        data = request.get_json() or {}

        profile = UserAppliances.query.filter_by(user_id=user_id).first()
        if not profile:
            return jsonify({"message": "No appliance profile found, use POST to create"}), 404

        for field in _FIELDS:
            if data.get(field) is not None:
                setattr(profile, field, data[field])

        profile.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify(profile.to_dict()), 200