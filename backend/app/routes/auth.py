import secrets, hashlib
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_mail import Message
from app.extensions import db, mail
from app.models.user import User
from app.models.reset_token import PasswordResetToken

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    district = data.get("district", "Colombo")

    if not name or not email or not password:
        return jsonify({"error": "Name, email and password are required"}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(name=name, email=email, password=password, district=district)
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user.to_dict()}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user.to_dict()}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    return jsonify({"user": user.to_dict()}), 200


@auth_bp.route("/change-password", methods=["PUT"])
@jwt_required()
def change_password():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    current = data.get("current_password", "")
    new_pw  = data.get("new_password", "")

    if not user.check_password(current):
        return jsonify({"error": "Current password is incorrect"}), 400

    if len(new_pw) < 6:
        return jsonify({"error": "New password must be at least 6 characters"}), 400

    if current == new_pw:
        return jsonify({"error": "New password must be different from current password"}), 400

    from app.extensions import bcrypt
    user.password_hash = bcrypt.generate_password_hash(new_pw).decode("utf-8")
    db.session.commit()
    return jsonify({"message": "Password changed successfully"}), 200


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    email = (request.get_json() or {}).get("email", "").strip().lower()
    user = User.query.filter_by(email=email).first()
    # Always return 200 to avoid revealing whether email exists
    if not user:
        return jsonify({"message": "If that email is registered, a reset link has been sent."}), 200

    # Delete any existing tokens for this user
    PasswordResetToken.query.filter_by(user_id=user.id).delete()

    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    reset = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=PasswordResetToken.make_expiry(),
    )
    db.session.add(reset)
    db.session.commit()

    frontend_url = current_app.config.get("FRONTEND_URL", "http://129.159.226.68:8080")
    reset_link = f"{frontend_url}/reset-password?token={raw_token}"

    msg = Message(
        subject="EnergyWise — Reset Your Password",
        recipients=[user.email],
        html=f"""
        <div style="font-family:sans-serif;max-width:480px;margin:auto">
          <h2 style="color:#2563eb">⚡ EnergyWise</h2>
          <p>Hi {user.name},</p>
          <p>We received a request to reset your password. Click the button below to set a new password.
             This link expires in <strong>1 hour</strong>.</p>
          <a href="{reset_link}"
             style="display:inline-block;background:#2563eb;color:#fff;padding:.75rem 1.5rem;
                    border-radius:6px;text-decoration:none;font-weight:600;margin:1rem 0">
            Reset Password
          </a>
          <p style="color:#64748b;font-size:.85rem">
            If you didn't request this, ignore this email — your password won't change.
          </p>
        </div>
        """,
    )
    try:
        mail.send(msg)
    except Exception as e:
        current_app.logger.error(f"Failed to send reset email: {e}")
    return jsonify({"message": "If that email is registered, a reset link has been sent."}), 200


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json() or {}
    raw_token = data.get("token", "")
    new_pw    = data.get("new_password", "")

    if len(new_pw) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    reset = PasswordResetToken.query.filter_by(token_hash=token_hash).first()

    if not reset or reset.is_expired():
        return jsonify({"error": "Reset link is invalid or has expired"}), 400

    user = User.query.get(reset.user_id)
    from app.extensions import bcrypt
    user.password_hash = bcrypt.generate_password_hash(new_pw).decode("utf-8")
    db.session.delete(reset)
    db.session.commit()
    return jsonify({"message": "Password reset successfully. You can now log in."}), 200
