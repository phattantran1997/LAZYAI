from mongoengine import connect
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/mentorship")

# Connect to MongoDB using MongoEngine
connect(host=MONGODB_URI) 