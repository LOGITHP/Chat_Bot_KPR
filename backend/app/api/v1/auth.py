from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from app.db.mongodb import db
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.core.permissions import get_current_user

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str

@router.post("/register")
async def register(request: RegisterRequest):
    existing_user = await db.users.find_one({"email": request.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    user_dict = {
        "email": request.email,
        "password_hash": get_password_hash(request.password),
        "name": request.name,
        "role": "student",
        "active": True
    }
    
    result = await db.users.insert_one(user_dict)
    return {"message": "User registered successfully", "id": str(result.inserted_id)}

@router.post("/login")
async def login(request: LoginRequest):
    user = await db.users.find_one({"email": request.email})
    if not user or not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
        
    access_token = create_access_token(subject=str(user["_id"]))
    refresh_token = create_refresh_token(subject=str(user["_id"]))
    
    # Store refresh token for revocation tracking if needed
    await db.sessions.insert_one({"user_id": str(user["_id"]), "refresh_token": refresh_token})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": user.get("role", "student")
    }

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    user_data = dict(current_user)
    user_data["_id"] = str(user_data["_id"])
    del user_data["password_hash"]
    return user_data
