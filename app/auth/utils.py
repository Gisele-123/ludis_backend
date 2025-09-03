from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import current_app
from flask_mail import Message
from ..extensions import mail
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask import jsonify

def generate_email_token(user_id: int, email: str) -> str:
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return s.dumps({"uid": user_id, "email": email}, salt="email-verify")

def verify_email_token(token: str, max_age: int):
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        data = s.loads(token, salt="email-verify", max_age=max_age)
        return data
    except SignatureExpired:
        return None
    except BadSignature:
        return None

def send_verification_email(user):
    token = generate_email_token(user.id, user.email)
    verify_link = f"{current_app.config['APP_BASE_URL']}/auth/verify-email?token={token}"

    msg = Message(
        subject="Ludis Email Verification",
        sender=current_app.config.get("MAIL_DEFAULT_SENDER"),
        recipients=[user.email],
        body=f"Hello {user.first_name},\n\nPlease verify your email by clicking this link:\n{verify_link}\n\nLink is valid for 24 hours.\n\nThanks,\nLudis Team"
    )
    mail.send(msg)
    current_app.logger.info(f"[EMAIL SENT] Verification email sent to {user.email}")
    return verify_link

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        identity = get_jwt_identity()
        if identity != "admin":
            return jsonify({"message": "Admin privileges required."}), 403
        return fn(*args, **kwargs)
    return wrapper