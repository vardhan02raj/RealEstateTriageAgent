from flask import Blueprint, request
from models.user_model import create_user, get_user_by_email, verify_password
from utils.token_utils import generate_access_token, generate_refresh_token
import jwt
from config import Config
from utils.validators import require_fields, valid_email, valid_password


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json

    missing = require_fields(data, ["name", "email", "password"])

    if missing:
        return {
            "success": False,
            "message": f"Missing fields: {missing}"
        }, 400

    if not valid_email(data["email"]):
        return {"success": False, "message": "Invalid email"}, 400

    if not valid_password(data["password"]):
        return {"success": False, "message": "Password too short"}, 400

    try:
        user_id = create_user(data)

        return {
            "success": True,
            "message": "User created",
            "data": {"user_id": user_id}
        }, 201

    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }, 400


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json

    if not data or not data.get("email") or not data.get("password"):
        return {"error": "Email and password required"}, 400

    if verify_password(data["email"], data["password"]):

        user = get_user_by_email(data["email"])

        access_token = generate_access_token(
            user["email"],
            user.get("role", "buyer")
        )

        refresh_token = generate_refresh_token(user["email"])

        return {
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token
        }, 200

    return {"error": "Invalid credentials"}, 401


@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    token = request.json.get("refresh_token")

    if not token:
        return {"error": "Missing refresh token"}, 400

    try:
        data = jwt.decode(
            token,
            Config.JWT_SECRET,
            algorithms=["HS256"]
        )

        if data.get("type") != "refresh":
            return {"error": "Invalid token type"}, 401

        user = get_user_by_email(data["email"])

        access_token = generate_access_token(
            user["email"],
            user.get("role", "buyer")
        )

        return {"access_token": access_token}, 200

    except Exception:
        return {"error": "Invalid refresh token"}, 401


@auth_bp.route("/user/<email>", methods=["GET"])
def get_user(email):
    user = get_user_by_email(email)

    if not user:
        return {"error": "User not found"}, 404

    return user, 200