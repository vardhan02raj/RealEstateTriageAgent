import re


def valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email)


def valid_password(password):
    return len(password) >= 6


def require_fields(data, fields):
    missing = [f for f in fields if not data.get(f)]
    return missing