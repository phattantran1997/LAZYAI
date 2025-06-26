from fastapi import APIRouter, HTTPException, status, Request, Response

from app.auth.jwt_handler import *
from app.schemas.user import UserRead

# ------------------- Router ---------------------------->

router = APIRouter(prefix="/auth", tags=["auth"])
    
# ------------------- Refresh Token ------------------------------->

@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_token(request: Request, response: Response):
#     token = request.cookies.get("refresh_token")
#     if token is None:
#         raise HTTPException(status_code=400 , detail="Login session has expired. Please log in again.")
#     returned_data = renew_access_token(token)
#     response.set_cookie("access_token", returned_data['access_token'], expires=returned_data['exp'], httponly=True, secure=False, samesite="lax")

    body = await request.json()
    token = body.get("token")
    if token is None:
        raise HTTPException(status_code=400, detail="Login session has expired. Please log in again.")
    returned_data = renew_access_token(token)
    return {
        "accessToken": returned_data['access_token'],
        "refreshToken": token
    }
