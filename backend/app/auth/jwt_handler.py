from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import HTTPException

# ---------------- JWT Configuration (for testing only) ---------------------------->

ALGORITHM = "HS256"

# Access Token Configuration
ACCESS_SECRET_KEY = "uhiuhuihohuihuihoiuoiuh"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # 30 minutes

# Refresh Token Configuration
REFRESH_SECRET_KEY = "asdasdasdasdasdasdawqdasd"
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30  # 30 days

# ------------------------- Access Token ---------------------------->

# Generate access token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, ACCESS_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Verify access token
def verify_access_token(token):
    if token is None:
        raise HTTPException(status_code=401, detail="Please login before uploading files") 
    try:
        payload = jwt.decode(token, ACCESS_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Your login session has expired. Please login again.") 

# Renew access token
def renew_access_token(token: str):
    data = verify_access_token(token)
    new_token = create_access_token(data)
    return new_token
    
# -------------------------- Refresh Token --------------------------->

# Create access token
def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Verify refresh token
def verify_refresh_token(token: str):
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials") 
