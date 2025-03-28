import psycopg2
import os
from dotenv import load_dotenv

# Load biến môi trường từ .env
load_dotenv()

POSTGRES_URI = os.getenv("POSTGRES_URL")  # VD: "postgresql://user:password@localhost:5432/mydatabase"

def connect_database():
    try:
        conn = psycopg2.connect(POSTGRES_URI)
        print("✅ PostgreSQL Connected")
        return conn
    except Exception as e:
        print("❌ Database connection error:", e)
        return None
