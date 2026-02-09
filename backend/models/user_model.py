from services.db import get_db
from datetime import datetime
import bcrypt

db = get_db()
users = db.users
users.create_index("email", unique=True)

def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)


def create_user(data):
    db = get_db()
    users = db.users

    # Prevent duplicate email
    if users.find_one({"email": data["email"]}):
        raise Exception("Email already registered")

    hashed_pw = hash_password(data["password"])

    user = {
        "name": data["name"],
        "email": data["email"],
        "password": hashed_pw,
        "role": data.get("role", "buyer"),
        "created_at": datetime.utcnow()
    }

    result = users.insert_one(user)
    return str(result.inserted_id)


def get_user_by_email(email):
    db = get_db()
    users = db.users

    user = users.find_one({"email": email})

    if user:
        user["_id"] = str(user["_id"])
        user.pop("password", None)  # hide password

    return user

def verify_password(email, password):
    db = get_db()
    users = db.users

    user = users.find_one({"email": email})

    if not user:
        return False

    stored_hash = user["password"]

    if bcrypt.checkpw(password.encode(), stored_hash):
        return True

    return False