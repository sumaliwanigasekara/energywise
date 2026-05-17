from functools import wraps
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User
from app.models.prediction import Prediction
from app.models.bill import Bill
from sqlalchemy import func

admin_bp = Blueprint("admin", __name__)


def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user or user.role != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper


@admin_bp.route("/stats", methods=["GET"])
@admin_required
def stats():
    total_users = User.query.filter_by(role="user").count()
    total_predictions = Prediction.query.count()
    avg_bill = db.session.query(func.avg(Prediction.predicted_bill)).scalar() or 0
    avg_units = db.session.query(func.avg(Prediction.predicted_units)).scalar() or 0

    risk_dist = (
        db.session.query(Prediction.risk_level, func.count(Prediction.id))
        .group_by(Prediction.risk_level)
        .all()
    )

    return jsonify({
        "total_users": total_users,
        "total_predictions": total_predictions,
        "avg_predicted_bill": round(float(avg_bill), 2),
        "avg_predicted_units": round(float(avg_units), 2),
        "risk_distribution": {r: c for r, c in risk_dist},
    }), 200


@admin_bp.route("/users", methods=["GET"])
@admin_required
def get_users():
    page = request.args.get("page", 1, type=int)
    users = (
        User.query.filter_by(role="user")
        .order_by(User.created_at.desc())
        .paginate(page=page, per_page=20, error_out=False)
    )
    result = []
    for u in users.items:
        d = u.to_dict()
        d["prediction_count"] = Prediction.query.filter_by(user_id=u.id).count()
        result.append(d)

    return jsonify({"users": result, "total": users.total, "pages": users.pages}), 200


@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == "admin":
        return jsonify({"error": "Cannot delete admin accounts"}), 400
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"}), 200


@admin_bp.route("/predictions", methods=["GET"])
@admin_required
def get_all_predictions():
    page = request.args.get("page", 1, type=int)
    predictions = (
        Prediction.query.order_by(Prediction.created_at.desc())
        .paginate(page=page, per_page=30, error_out=False)
    )
    return jsonify({
        "predictions": [p.to_dict() for p in predictions.items],
        "total": predictions.total,
        "pages": predictions.pages,
    }), 200
