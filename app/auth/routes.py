from flask import Blueprint, request, jsonify, current_app
from email_validator import validate_email, EmailNotValidError
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..extensions import db
from ..models import User
from .utils import send_verification_email, verify_email_token
from ..config import Config

auth_bp = Blueprint("auth", __name__)

# ---------- Helpers ----------
def _json_required(*fields):
    data = request.get_json(silent=True) or {}
    missing = [f for f in fields if not data.get(f)]
    if missing:
        return None, jsonify({"message": f"Missing fields: {', '.join(missing)}"}), 400
    return data, None, None

# ---------- Routes ----------
@auth_bp.post("/register")
def register():
    data, err_resp, status = _json_required("first_name", "last_name", "email", "phone", "password")
    if err_resp:
        return err_resp, status

    try:
        data["email"] = validate_email(data["email"], check_deliverability=False).email
    except EmailNotValidError as e:
        return jsonify({"message": str(e)}), 400

    if len(data["phone"]) < 7:
        return jsonify({"message": "Phone number looks too short."}), 400

    user = User(
        first_name=data["first_name"].strip(),
        last_name=data["last_name"].strip(),
        email=data["email"].lower().strip(),
        phone=data["phone"].strip(),
    )
    user.set_password(data["password"])

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Email or phone already in use."}), 409

    # Send real email
    send_verification_email(user)

    return jsonify({
        "message": "Registration successful. Verification email sent.",
        "user": user.to_safe_dict()
    }), 201

@auth_bp.get("/verify-email")
def verify_email():
    token = request.args.get("token")
    if not token:
        return jsonify({"message": "Missing token."}), 400

    data = verify_email_token(token, current_app.config["EMAIL_TOKEN_MAX_AGE"])
    if not data:
        return jsonify({"message": "Invalid or expired token."}), 400

    user = User.query.get(data["uid"])
    if not user or user.email != data["email"]:
        return jsonify({"message": "Token does not match any user."}), 400

    if user.is_email_verified:
        return jsonify({"message": "Email already verified."}), 200

    user.is_email_verified = True
    db.session.commit()
    return jsonify({"message": "Email verified successfully."}), 200


@auth_bp.post("/login")
def login():
    data, err_resp, status = _json_required("email", "password")
    if err_resp:
        return err_resp, status

    email = data["email"].lower().strip()
    password = data["password"]

    # Admin check
    if email == Config.ADMIN_EMAIL.lower() and password == Config.ADMIN_PASSWORD:
        access_token = create_access_token(identity="admin")
        return jsonify({
            "access_token": access_token,
            "user": {
                "id": "admin",
                "email": Config.ADMIN_EMAIL,
                "role": "admin"
            }
        }), 200

    # Regular user
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid credentials."}), 401

    if not user.is_email_verified:
        return jsonify({"message": "Email not verified. Please verify your email first."}), 403

    access_token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": access_token, "user": user.to_safe_dict()}), 200


@auth_bp.get("/me")
@jwt_required()
def me():
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    if not user:
        return jsonify({"message": "User not found."}), 404
    return jsonify({"user": user.to_safe_dict()}), 200
