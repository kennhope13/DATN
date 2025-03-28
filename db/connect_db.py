from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()
MONGO_URI = os.getenv("URL_DB")

def connect_database():
    try:
        # Kết nối MongoDB
        client = MongoClient(MONGO_URI)
        print("✅ MongoDB Connected")
        return client  # Trả về đối tượng client để thao tác với DB
    except Exception as e:
        print("❌ Database connection error:", e)
        return None

