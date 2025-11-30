import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/schoolify")

client = MongoClient(MONGODB_URI)

_default_db = client.get_default_database()
db = _default_db if _default_db is not None else client["schoolify"]

def get_users_collection():
    return db["users"]

def ping():
    """Return True if Mongo responds to ping."""
    try:
        client.admin.command("ping")
        return True
    except Exception:
        return False