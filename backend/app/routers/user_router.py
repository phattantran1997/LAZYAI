from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Depends

from app.schemas.user import *
from app.services.user import *

from app.auth.jwt_handler import get_current_token

# ----------------------- Router -------------------------------->

router = APIRouter(prefix="/users", tags=["users"])

# --------------------------- Create / Register / Login / Logout--------------------------------->

# Create | Register new User
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user_endpoint(user_input: UserRegister) -> dict:
    try:
        register_user(user_input)
        return {"message": "User registered successfully"} 
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Login endpoint
@router.post("/login", status_code=status.HTTP_200_OK)
async def login_user_endpoint(user_input: UserLogin, response: Response):
    try:
        result = login_user(user_input)
        data_access = result['data_access_token']
        data_refresh = result['data_refresh_token']
        user = result["user"]

        # #response.set_cookie("access_token", data_access['access_token'], expires=data_access['exp'], httponly=True, secure=False, samesite="lax")
        # #response.set_cookie("refresh_token", data_refresh['refresh_token'], expires=data_refresh['exp'], httponly=True, secure=False, samesite="lax")

        # return user

        return {
            "access_token": data_access['access_token'],
            "refresh_token": data_refresh["refresh_token"],
            "token_type": "bearer",
            "user": user
        }
    
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    
# Log out endpoint
@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_user_endpoint(response: Response):
    try:
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

# --------------------------- Read ------------------------------>

# Get a user by ID
@router.get("/get/{user_id}", response_model=UserRegister)
async def get_user_endpoint(user_id: str):
    try:
        user = get_user_by_id(user_id)
        return user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Get current user
# @router.get("/me", status_code=status.HTTP_200_OK)
# def get_current_user_endpoint(request: Request):
    # token = request.cookies.get("access_token")
    # if token is None:
    #     raise HTTPException(status_code=401, detail="Access token has expired")
    # try:
    #     user = get_current_user(token)
    #     return user
    # except Exception:
    #     raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/me", status_code=status.HTTP_200_OK)
def get_current_user_endpoint(token: dict = Depends(get_current_token)):
    return token['data']

# --------------------------- Update -------------------------------->
 
@router.put("/put/{user_id}", response_model=UserRegister)
async def update_user_endpoint(user_id: str, user_input: UserUpdate):
    try:
        user = update_user(user_id, user_input)
        return user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# -------------------------- Delete -------------------------------->

@router.delete("/delete/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_endpoint(user_id: str):
    try:
        delete_user(user_id)
        return {"message": "User deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    