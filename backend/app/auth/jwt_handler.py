from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException

from app.schemas.user import UserRead

# ---------------- JWT Configuration (for testing only) ---------------------------->

ALGORITHM = "HS256"

# Access Token Configuration
ACCESS_SECRET_KEY = "uhiuhuihohuihuihoiuoiuh"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # 30 minutes

# Refresh Token Configuration
REFRESH_SECRET_KEY = "asdasdasdasdasdasdawqdasd"
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30  # 30 days

# Help to extract the headers
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

# ------------------------ Get Current Token ------------------------>

def get_current_token(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Access token missing")
    try:
        user = verify_access_token(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
    return {
        "token": token,
        "data": user
    }

# ------------------------- Access Token ---------------------------->

# Generate access token
def create_access_token(data: UserRead) -> dict:
    to_encode = data.model_dump()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, ACCESS_SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": encoded_jwt,
        "exp": expire
    }


# Verify access token
def verify_access_token(token) -> UserRead:
    if token is None:
        raise HTTPException(status_code=401, detail="Access token has expired") 
    try:
        payload = jwt.decode(token, ACCESS_SECRET_KEY, algorithms=[ALGORITHM])
        return UserRead(**payload)
    except JWTError:
        raise HTTPException(status_code=401, detail="Your login session has expired. Please login again.") 
    

# Renew access token
def renew_access_token(token: str) -> dict:
    data = verify_refresh_token(token)
    returned_data = create_access_token(data)
    return returned_data
    
# -------------------------- Refresh Token --------------------------->

# Create access token
def create_refresh_token(data: UserRead) -> dict:
    to_encode = data.model_dump()
    expire = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)

    return {
        "refresh_token": encoded_jwt,
        "exp": expire
    }

# Verify refresh token
def verify_refresh_token(token: str) -> UserRead:
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        return UserRead(**payload)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials") 

