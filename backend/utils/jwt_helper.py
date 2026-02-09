import jwt
import datetime
from config import Config

def generate_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=Config.JWT_EXPIRY)
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")

def decode_token(token):
    return jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])