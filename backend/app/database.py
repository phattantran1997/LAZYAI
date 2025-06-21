from mongoengine import connect, disconnect
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/mydb")

def connect_db():
    try:
        connect(host=MONGODB_URI, alias="default")
        print("MongoDB connected.")
    except Exception as e:
        print(f"MongoDB connection error: {e}")

def disconnect_db():
    try:
        disconnect(alias="default")
        print("MongoDB disconnected.")
    except Exception as e:
        print(f"MongoDB disconnection error: {e}")