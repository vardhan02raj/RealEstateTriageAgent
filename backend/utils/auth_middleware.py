from functools import wraps
from flask import request, jsonify
import jwt
from config import Config


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = None

        # Token comes from header
        if "Authorization" in request.headers:
            bearer = request.headers["Authorization"]
            parts = bearer.split()

            if len(parts) == 2 and parts[0] == "Bearer":
                token = parts[1]

        if not token:
            return jsonify({"error": "Token missing"}), 401

        try:
            data = jwt.decode(
                token,
                Config.JWT_SECRET,
                algorithms=["HS256"]
            )

            # attach user info to request
            request.user = data

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401

        except Exception:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated