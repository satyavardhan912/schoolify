import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://mongo:27017/schoolify")

client = MongoClient(MONGODB_URI)

db = client.get_default_database() if client.get_default_database() else client["schoolify"]

def get_users_collection():
    return db["users"]