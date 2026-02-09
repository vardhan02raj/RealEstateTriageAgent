from flask import Blueprint, request
from models.user_model import create_user, get_user_by_email, verify_password
from utils.token_utils import generate_token
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
        token = generate_token(data["email"])

        return {
            "message": "Login successful",
            "token": token
        }, 200

    return {"error": "Invalid credentials"}, 401


@auth_bp.route("/user/<email>", methods=["GET"])
def get_user(email):
    user = get_user_by_email(email)

    if not user:
        return {"error": "User not found"}, 404

    return user