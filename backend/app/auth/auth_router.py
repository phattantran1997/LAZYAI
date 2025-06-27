from fastapi import APIRouter, status, Request, Response

from app.auth.jwt_handler import *

# ------------------- Router ---------------------------->

router = APIRouter(prefix="/auth", tags=["auth"])
    
# ------------------- Refresh Token ------------------------------->

@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_token(request: Request):
#     token = request.cookies.get("refresh_token")
#     if token is None:
#         raise HTTPException(status_code=400 , detail="Login session has expired. Please log in again.")
#     returned_data = renew_access_token(token)
#     response.set_cookie("access_token", returned_data['access_token'], expires=returned_data['exp'], httponly=True, secure=False, samesite="lax")

    token = request.headers.get("x-refresh-token")
    if not token:
        raise HTTPException(status_code=404, detail="Please login again.")
    returned_data = renew_access_token(token)
    # return {
    #     "accessToken": returned_data['access_token'],
    #     "refreshToken": token
    # }
    return {"access_token": returned_data['access_token']}
