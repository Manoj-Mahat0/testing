import bcrypt
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from config import SECRET_KEY, ALGORITHM

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_token(email: str, is_admin: bool):
    expiration = datetime.utcnow() + timedelta(days=1)
    token = jwt.encode(
        {"sub": email, "is_admin": is_admin, "exp": expiration},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return token

def get_current_user(token: str):
    """Accepts a token string and validates it."""
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
