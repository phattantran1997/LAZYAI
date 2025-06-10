from fastapi import APIRouter, HTTPException, Depends
from typing import List
from bson import ObjectId
from app.models.user import UserCreate, UserInDB, UserResponse
from app.database import database
from datetime import datetime

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate):
    # Check if user already exists
    if await database.users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user document
    user_dict = user.model_dump()
    user_dict["created_at"] = datetime.utcnow()
    user_dict["updated_at"] = datetime.utcnow()
    
    # Insert into database
    result = await database.users.insert_one(user_dict)
    
    # Get created user and convert _id to id
    created_user = await database.users.find_one({"_id": result.inserted_id})
    if created_user:
        created_user["id"] = str(created_user.pop("_id"))
        return UserResponse(**created_user)
    raise HTTPException(status_code=500, detail="Failed to create user")

@router.get("/", response_model=List[UserResponse])
async def get_users():
    users = await database.users.find().to_list(length=100)
    # Convert _id to id for each user
    for user in users:
        user["id"] = str(user.pop("_id"))
    return [UserResponse(**user) for user in users]

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    user = await database.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Convert _id to id
    user["id"] = str(user.pop("_id"))
    return UserResponse(**user)

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user: UserCreate):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    # Check if user exists
    existing_user = await database.users.find_one({"_id": ObjectId(user_id)})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user
    update_data = user.model_dump()
    update_data["updated_at"] = datetime.utcnow()
    
    await database.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    
    # Get updated user and convert _id to id
    updated_user = await database.users.find_one({"_id": ObjectId(user_id)})
    if updated_user:
        updated_user["id"] = str(updated_user.pop("_id"))
        return UserResponse(**updated_user)
    raise HTTPException(status_code=500, detail="Failed to update user")

@router.delete("/{user_id}")
async def delete_user(user_id: str):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    result = await database.users.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User deleted successfully"} 