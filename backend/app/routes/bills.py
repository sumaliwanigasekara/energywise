from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.bill import Bill

bills_bp = Blueprint("bills", __name__)


@bills_bp.route("/bills", methods=["GET"])
@jwt_required()
def get_bills():
    user_id = int(get_jwt_identity())
    bills = Bill.query.filter_by(user_id=user_id).order_by(Bill.year.desc(), Bill.month.desc()).all()
    return jsonify({"bills": [b.to_dict() for b in bills]}), 200


@bills_bp.route("/bills", methods=["POST"])
@jwt_required()
def add_bill():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    month = data.get("month")
    year = data.get("year")
    amount = data.get("amount")

    if not all([month, year, amount]):
        return jsonify({"error": "month, year and amount are required"}), 400

    bill = Bill(
        user_id=user_id,
        month=int(month),
        year=int(year),
        units=float(data.get("units") or 0),
        amount=float(amount),
        notes=data.get("notes", ""),
    )
    db.session.add(bill)
    db.session.commit()
    return jsonify({"bill": bill.to_dict()}), 201


@bills_bp.route("/bills/<int:bill_id>", methods=["PUT"])
@jwt_required()
def update_bill(bill_id):
    user_id = int(get_jwt_identity())
    bill = Bill.query.filter_by(id=bill_id, user_id=user_id).first_or_404()
    data = request.get_json()

    bill.month = int(data.get("month", bill.month))
    bill.year = int(data.get("year", bill.year))
    bill.units = float(data.get("units") or bill.units)
    bill.amount = float(data.get("amount", bill.amount))
    bill.notes = data.get("notes", bill.notes)

    db.session.commit()
    return jsonify({"bill": bill.to_dict()}), 200


@bills_bp.route("/bills/<int:bill_id>", methods=["DELETE"])
@jwt_required()
def delete_bill(bill_id):
    user_id = int(get_jwt_identity())
    bill = Bill.query.filter_by(id=bill_id, user_id=user_id).first_or_404()
    db.session.delete(bill)
    db.session.commit()
    return jsonify({"message": "Bill deleted"}), 200
