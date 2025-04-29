from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from app.routers import ask, quiz
from app.routers.ask_router import router as ask_router

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/mydb")
client = AsyncIOMotorClient(MONGODB_URI)
database = client.mentorship

# Include routers
app.include_router(ask.router)
app.include_router(quiz.router)
app.include_router(ask_router)

# Health-check route
@app.get("/health")
async def health_check():
    return {"status": "ok"} 