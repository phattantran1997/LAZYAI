from app.routers.user_router import router as user_router
from app.routers.ask_router  import router as ask_router
from app.routers.quiz_router import router as quiz_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import app.database  # Import to establish database connection

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

# Include routers
app.include_router(quiz_router)
app.include_router(ask_router)
app.include_router(user_router)

# Health-check route
@app.get("/health")
async def health_check():
    return {"status": "ok"} 