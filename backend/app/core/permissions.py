from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_token
from app.db.mongodb import db
from bson import ObjectId

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
        
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
        
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise credentials_exception
        
    if not user.get("active", True):
        raise HTTPException(status_code=400, detail="Inactive user")
        
    return user

async def get_current_active_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="The user doesn't have enough privileges")
    return current_user

async def get_current_active_faculty(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") not in ["admin", "faculty"]:
        raise HTTPException(status_code=403, detail="The user doesn't have enough privileges")
    return current_user
