from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.prediction import Prediction

history_bp = Blueprint("history", __name__)


@history_bp.route("/predictions", methods=["GET"])
@jwt_required()
def get_predictions():
    user_id = int(get_jwt_identity())
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    paginated = (
        Prediction.query.filter_by(user_id=user_id)
        .order_by(Prediction.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return jsonify({
        "predictions": [p.to_dict() for p in paginated.items],
        "total": paginated.total,
        "pages": paginated.pages,
        "current_page": page,
    }), 200


@history_bp.route("/predictions/<int:prediction_id>", methods=["GET"])
@jwt_required()
def get_prediction(prediction_id):
    user_id = int(get_jwt_identity())
    p = Prediction.query.filter_by(id=prediction_id, user_id=user_id).first_or_404()
    return jsonify(p.to_dict()), 200


@history_bp.route("/predictions/<int:prediction_id>", methods=["DELETE"])
@jwt_required()
def delete_prediction(prediction_id):
    user_id = int(get_jwt_identity())
    p = Prediction.query.filter_by(id=prediction_id, user_id=user_id).first_or_404()
    db.session.delete(p)
    db.session.commit()
    return jsonify({"message": "Prediction deleted"}), 200


@history_bp.route("/predictions/<int:prediction_id>/actual", methods=["PATCH"])
@jwt_required()
def update_actual(prediction_id):
    user_id = int(get_jwt_identity())
    p = Prediction.query.filter_by(id=prediction_id, user_id=user_id).first_or_404()
    data = request.get_json() or {}
    actual_units = data.get("actual_units")
    if actual_units is None or float(actual_units) <= 0:
        return jsonify({"error": "actual_units must be a positive number"}), 400
    from app.services.tariff_service import calculate_bill
    p.actual_units = round(float(actual_units), 2)
    p.actual_bill  = round(calculate_bill(p.actual_units), 2)
    db.session.commit()
    return jsonify(p.to_dict()), 200


@history_bp.route("/predictions/autofill", methods=["GET"])
@jwt_required()
def autofill():
    """Pre-fill past 3 months from the most recent prediction.
    - prev_bill_1 = that prediction's actual_units (if entered) or predicted_units
    - prev_bill_2 = what the user entered as prev_bill_1 in that prediction
    - prev_bill_3 = what the user entered as prev_bill_2 in that prediction
    This means even a single past prediction fills all 3 fields.
    """
    user_id = int(get_jwt_identity())
    last = (
        Prediction.query.filter_by(user_id=user_id)
        .order_by(Prediction.created_at.desc())
        .first()
    )
    if not last:
        return jsonify({"prev_bill_1": None, "prev_bill_2": None, "prev_bill_3": None, "source": []}), 200

    bill_1 = last.actual_units if last.actual_units else last.predicted_units
    bill_2 = last.prev_bill_1
    bill_3 = last.prev_bill_2

    src_1 = "actual" if last.actual_units else "predicted"

    return jsonify({
        "prev_bill_1": round(bill_1, 1) if bill_1 else None,
        "prev_bill_2": round(bill_2, 1) if bill_2 else None,
        "prev_bill_3": round(bill_3, 1) if bill_3 else None,
        "source": [src_1, "from your entry", "from your entry"],
    }), 200
