import jwt
from datetime import datetime, timedelta, timezone
from flask import current_app

def generate_token(user_uid, expires_in=3600):
    payload = {
        "uid": user_uid,
        "exp": datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    }
    token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")
    return token

def decode_token(token):
    return jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
