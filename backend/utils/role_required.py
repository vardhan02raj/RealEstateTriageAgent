from functools import wraps
from flask import request, jsonify


def role_required(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):

            user_role = request.user.get("role")

            if user_role not in roles:
                return jsonify({"error": "Access denied"}), 403

            return f(*args, **kwargs)

        return decorated
    return wrapper