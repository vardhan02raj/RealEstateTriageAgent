from flask import Blueprint, request
from services.db import get_db
from utils.token_utils import token_required

health_bp = Blueprint("health", __name__)

@health_bp.route("/")
def home():
    db = get_db()
    return {
        "status": "Backend alive 🚀",
        "database": db.name
    }

@health_bp.route("/secure", methods=["GET"])
@token_required
def secure():
    return {
        "message": "You accessed protected route",
        "user": request.user
    }