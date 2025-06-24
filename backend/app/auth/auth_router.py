from fastapi import APIRouter, HTTPException, status, Request, Response

from app.auth.jwt_handler import *
from app.schemas.user import UserRead

# ------------------- Router ---------------------------->

router = APIRouter(prefix="/auth", tags=["auth"])

# ------------------- Get Current User ---------------------------->

@router.get("/me", status_code=status.HTTP_200_OK)
def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if token is None:
        raise HTTPException(status_code=401 , detail="Access token has expired")
    try:
        data = verify_access_token(token)
        return UserRead(**data)
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    
# ------------------- Refresh Token ------------------------------->

@router.get("/refresh", status_code=status.HTTP_200_OK)
def refresh_token(request: Request, response: Response):
    token = request.cookies.get("refresh_token")
    if(token is None):
        raise HTTPException(status_code=400 , detail="Login session has expired. Please log in again.")
    new_access_token = renew_access_token(token)
    response.set_cookie("access_token", new_access_token, httponly=True, secure=False, samesite="lax")


