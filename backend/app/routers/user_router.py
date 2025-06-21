from fastapi import APIRouter, HTTPException, status

from app.schemas.user import *
from app.services.user import *

# ----------------------- Router -------------------------------->

router = APIRouter(prefix="/users", tags=["users"])

# --------------------------- Create / Register / Login --------------------------------->

# Create | Register new User
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user_endpoint(user_input: UserRegister):
    try:
        user = register_user(user_input)
        return {"message": "User registered successfully", "user_id": str(user.id)} # type: ignore
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Login endpoint
@router.post("/login", status_code=status.HTTP_200_OK)
async def login_user_endpoint(user_input: UserLogin):
    try:
        result = login_user(user_input)
        return result
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

# --------------------------- Read ------------------------------>

# Get a user by ID
@router.get("/{user_id}", response_model=UserRegister)
async def get_user_endpoint(user_id: str):
    try:
        user = get_user_by_id(user_id)
        return user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# --------------------------- Update -------------------------------->
 
@router.put("/{user_id}", response_model=UserRegister)
async def update_user_endpoint(user_id: str, user_input: UserUpdate):
    try:
        user = update_user(user_id, user_input)
        return user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# -------------------------- Delete -------------------------------->

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_endpoint(user_id: str):
    try:
        delete_user(user_id)
        return {"message": "User deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
