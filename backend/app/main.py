from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.routers.user_router import router as user_router
from app.routers.file_router import router as file_router
from app.routers.ask_router  import router as ask_router
from app.routers.quiz_router import router as quiz_router

from fastapi.middleware.cors import CORSMiddleware
from app.database import connect_db, disconnect_db  # Updated import

@asynccontextmanager
async def lifespan(app: FastAPI):
    connect_db()
    yield
    disconnect_db()

app = FastAPI(lifespan=lifespan)

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
app.include_router(file_router)

# Health-check route
@app.get("/health")
async def health_check():
    return {"status": "ok"}