import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load .env file
load_dotenv()

def get_db():
    mongo_host = os.getenv("MONGO_HOST", "localhost:27017")
    mongo_db = os.getenv("MONGO_DB", "books_db")

    # Build URI
    uri = f"mongodb://{mongo_host}/{mongo_db}"

    client = MongoClient(uri)
    return client[mongo_db]

def get_books_collection():
    db = get_db()
    return db["books"]

def get_changelog_collection():
    db = get_db()
    return db["changes"]

