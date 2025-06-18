from passlib.context import CryptContext
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from mongoengine.errors import NotUniqueError
from app.request.UserLogin import UserLogin
from app.request.UserRegister import UserRegister
from app.auth.jwt_handler import create_access_token
from datetime import timedelta
#------------------------ Password Hashing ------------------------>

# Password hashing context (using bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Helper function to hash passwords
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Helper function to verify passwords
def compare_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# ------------------------ CRUD Operations ------------------------>

# Create a new user
def create_user(user_in: UserRegister) -> User:
    # Check if email or username already exists
    if User.objects(email=user_in.email).first():
        raise ValueError("Email already registered")
    if User.objects(username=user_in.username).first():
        raise ValueError("Username already taken")

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

# ------------------------------------------------------------------>

# Get a user by ID
def get_user_by_id(user_id: str) -> User:
    user = User.objects(id=user_id).first()
    if not user:
        raise ValueError("User not found")
    return user

# Get all users (optional)
def get_all_users(skip: int = 0, limit: int = 100) -> list:
    users = User.objects.skip(skip).limit(limit)
    return users

# ------------------------------------------------------------------>

# Update a user
def update_user(user_id: str, user_in: UserUpdate) -> User:
    user = User.objects(id=user_id).first()
    if not user:
        raise ValueError("User not found")

    # Update fields if provided
    if user_in.username:
        user.username = user_in.username
    if user_in.name:
        user.name = user_in.name
    if user_in.email:
        user.email = user_in.email
    if user_in.role:
        user.role = user_in.role
    if user_in.is_active is not None:
        user.is_active = user_in.is_active

    user.save()
    return user

# ------------------------------------------------------------------>

# Delete a user
def delete_user(user_id: str) -> bool:
    user = User.objects(id=user_id).first()
    if not user:
        raise ValueError("User not found")
    user.delete()
    return True

#Login User
def login_user(userLogin: UserLogin) -> dict:
    user = User.objects(username=userLogin.username).first()
    if not user:
        raise ValueError("User not found")
    if not compare_password(userLogin.password, user.password):
        raise ValueError("Invalid password")
    
    # Create JWT token
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role, "user_id": str(user.id)}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "username": user.username,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }

def register_user(userRegister: UserRegister) -> User:
    user = User.objects(username=userRegister.username).first()
    if user:
        raise ValueError("User already exists")
    return create_user(userRegister)
