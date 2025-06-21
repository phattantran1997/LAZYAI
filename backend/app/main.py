from app.routers.user_router import router as user_router
# from app.routers.file_router import router as file_router
from app.routers.ask_router  import router as ask_router
from app.routers.quiz_router import router as quiz_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import connect_db, disconnect_db  # Updated import

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to DB on startup
@app.on_event("startup")
async def startup_event():
    connect_db()

# Disconnect from DB on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    disconnect_db()

# Include routers
app.include_router(quiz_router)
app.include_router(ask_router)
app.include_router(user_router)
# app.include_router(file_router)

# Health-check route
@app.get("/health")
async def health_check():
    return {"status": "ok"}