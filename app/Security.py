import os
import time

from dotenv import load_dotenv
from passlib.context import CryptContext
from jose import jwt, JWTError

load_dotenv()

# BCrypt config
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a plain password."""
    return pwd_ctx.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against the stored hash."""
    return pwd_ctx.verify(plain_password, hashed_password)

# JWT config
JWT_SECRET = os.getenv("JWT_SECRET", "please-change-this-secret")
ALGORITHM = "HS256"
ISSUER = os.getenv("JWT_ISSUER", "schoolify")
AUDIENCE = os.getenv("JWT_AUD", "schoolify")
ACCESS_TOKEN_EXPIRE_SECONDS = int(os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS", "3600"))

def create_access_token(subject: str, role: str) -> str:
    now = int(time.time())
    payload = {
        "sub": str(subject),
        "role": role,
        "iss": ISSUER,
        "aud": AUDIENCE,
        "iat": now,
        "exp": now + ACCESS_TOKEN_EXPIRE_SECONDS,
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)
    return token

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM], issuer=ISSUER, audience=AUDIENCE)
        return payload
    except JWTError as e:
        raise