from fastapi import HTTPException
from passlib.context import CryptContext
from app.auth.jwt_handler import create_access_token, create_refresh_token, verify_access_token

from app.models.user import User
from app.schemas.user import *

#------------------------ Password Hashing ------------------------>

# Context for password  |  Algorithm: bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hashing passwords
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Verify passwords
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# ------------------------ Create / Register ------------------------>

# Create a new user
def create_user(user_in: UserRegister) -> User:

    # Check if user already exists
    if User.objects(email=user_in.email).first():  # type: ignore
        raise HTTPException(status_code=403, detail="Email already registered")
    if User.objects(username=user_in.username).first(): # type: ignore
        raise HTTPException(status_code=403, detail="Username already taken")

    # Hash the password before storing it
    hashed_password = hash_password(user_in.password)

    # Create and save the new user in the database
    user = User(
        username=user_in.username,
        name=user_in.name,
        email=user_in.email,
        password=hashed_password,
        role=user_in.role
    )
    user.save()  # Save the user in the database

    return user

# ---------------------------- Read -------------------------------->

# Get a user by ID
def get_user_by_id(user_id: str) -> User:
    user = User.objects(id=user_id).first() # type: ignore
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Get data from current user
def get_current_user(token: str) -> UserRead:
    return verify_access_token(token)

# -------------------------- Update ---------------------------------->

# Update a user
def update_user(user_id: str, user_input: UserUpdate) -> User:
    user = User.objects(id=user_id).first() # type: ignore
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update fields if provided
    if user_input.username:
        user.username = user_input.username
    if user_input.name:
        user.name = user_input.name
    if user_input.email:
        user.email = user_input.email
    if user_input.role:
        user.role = user_input.role
    if user_input.is_active is not None:
        user.is_active = user_input.is_active

    user.save()
    return user

# ------------------------- Delete --------------------------------->

# Delete a user
def delete_user(user_id: str) -> bool:
    user = User.objects(id=user_id).first() # type: ignore
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.delete()
    return True

# ----------------------- Log In and Register ----------------------------->

# Login User
def login_user(userLogin: UserLogin) -> dict:

    # Check if the user exists
    user = User.objects(username=userLogin.username).first() # type: ignore
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(userLogin.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    user_data = UserRead(
        username=user.username,
        email=user.email,
        role=user.role
    )

    # Create JWT token and set expire time
    access_token = create_access_token(user_data)
    refresh_token = create_refresh_token(user_data)

    return {
            "data_access_token": access_token,
            "data_refresh_token": refresh_token,
            "user": user_data
        }

# Register | Create new User
def register_user(userRegister: UserRegister) -> User:
    return create_user(userRegister)
