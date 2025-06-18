# app/routers/user_router.py
from typing import List
from fastapi import APIRouter, HTTPException, status
from app.schemas.user import UserCreate, UserUpdate, UserRead
from app.services.userService import *
from app.request.UserLogin import UserLogin
from app.request.UserRegister import UserRegister

router = APIRouter(prefix="/users", tags=["users"])

# ---------------------------------------------------------------->

# Create a new user
@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(user_in: UserCreate):
    try:
        user = create_user(user_in)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ---------------------------------------------------------------->

# Get a user by ID
@router.get("/{user_id}", response_model=UserRead)
async def get_user_endpoint(user_id: str):
    try:
        user = get_user_by_id(user_id)
        return user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Get all users (optional)
@router.get("/", response_model=List[UserRead])
async def get_users_endpoint(skip: int = 0, limit: int = 100):
    users = get_all_users(skip, limit)
    return users

# ---------------------------------------------------------------->

# Update a user by ID
@router.put("/{user_id}", response_model=UserRead)
async def update_user_endpoint(user_id: str, user_in: UserUpdate):
    try:
        user = update_user(user_id, user_in)
        return user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# ---------------------------------------------------------------->

# Delete a user by ID
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_endpoint(user_id: str):
    try:
        delete_user(user_id)
        return {"message": "User deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# ---------------------------------------------------------------->

#Login User
@router.post("/login", status_code=status.HTTP_200_OK)
async def login_user_endpoint(user_in: UserLogin):
    try:
        result = login_user(user_in)
        return result
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

#Register User
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user_endpoint(user_in: UserRegister):
    try:
        user = register_user(user_in)
        return {"message": "User registered successfully", "user_id": str(user.id)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
