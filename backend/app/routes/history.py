from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
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
