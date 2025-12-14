import base64
import hashlib
import os
import logging

try:
    from cryptography.fernet import Fernet, InvalidToken
except Exception:
    Fernet = None
    InvalidToken = Exception

logger = logging.getLogger("app.crypto")
password = "satyavardhan"
hashed_key_digest = hashlib.sha256(password.encode('utf-8')).digest()
_key = base64.urlsafe_b64encode(hashed_key_digest)
_fernet = None

if _key and Fernet is not None:
    try:
        _fernet = Fernet(_key.encode() if isinstance(_key, str) else _key)
    except Exception as e:
        logger.warning("Failed to initialize Fernet with provided FIELD_ENCRYPTION_KEY: %s", e)
        _fernet = None
else:
    if Fernet is None:
        logger.warning("cryptography package not available. Field encryption disabled.")
    else:
        logger.warning("FIELD_ENCRYPTION_KEY not set. Field encryption disabled (no-op).")

def encrypt_field(plaintext: str) -> str | None:
    """Encrypt a plaintext string. Returns base64 ciphertext string or None if input is falsy."""
    if plaintext is None:
        return None
    if _fernet is None:
        return plaintext  # no-op fallback
    if not isinstance(plaintext, (str, bytes)):
        plaintext = str(plaintext)
    try:
        token = _fernet.encrypt(plaintext.encode("utf-8"))
        return token.decode("utf-8")
    except Exception as e:
        logger.exception("encrypt_field error: %s", e)
        return plaintext

def decrypt_field(ciphertext: str) -> str | None:
    """Decrypt a ciphertext produced by encrypt_field. Returns plaintext string or None."""
    if ciphertext is None:
        return None
    if _fernet is None:
        return ciphertext
    try:
        plain = _fernet.decrypt(ciphertext.encode("utf-8"))
        return plain.decode("utf-8")
    except InvalidToken:
        logger.warning("decrypt_field: Invalid token or wrong key. Returning raw value.")
        return ciphertext
    except Exception as e:
        logger.exception("decrypt_field error: %s", e)
        return ciphertext