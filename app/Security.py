import os
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()

# BCrypt config
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a plain password."""
    return pwd_ctx.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against the stored hash."""
    return pwd_ctx.verify(plain_password, hashed_password)