import jwt
import datetime
import os
from functools import wraps
from flask import request


SECRET = os.getenv("JWT_SECRET")


import jwt
from datetime import datetime, timedelta
from config import Config


def generate_access_token(email, role):
    payload = {
        "email": email,
        "role": role,
        "exp": datetime.utcnow() + timedelta(minutes=15)
    }

    return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")


def generate_refresh_token(email):
    payload = {
        "email": email,
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(days=7)
    }

    return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")


# 🔒 Auth decorator
def token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        token = request.headers.get("Authorization")

        if not token:
            return {"error": "Token missing"}, 401

        try:
            decoded = jwt.decode(token, SECRET, algorithms=["HS256"])
            request.user = decoded["email"]

        except jwt.ExpiredSignatureError:
            return {"error": "Token expired"}, 401

        except jwt.InvalidTokenError:
            return {"error": "Invalid token"}, 401

        return func(*args, **kwargs)

    return wrapper