import time
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, Security, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import config
from database.mongo import db_manager

try:
    from jose import jwt, JWTError
    JOSE_AVAILABLE = True
except ImportError:
    JOSE_AVAILABLE = False

security = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    """Hashes passwords securely using SHA-256 with salt."""
    salted = f"{password}{config.SECRET_KEY}"
    return hashlib.sha256(salted.encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    
    if JOSE_AVAILABLE:
        return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    else:
        # Fallback simple token
        return f"mock_token_{to_encode.get('sub')}_{to_encode.get('role')}_{int(time.time())}"

def decode_token(token: str) -> Dict[str, Any]:
    if JOSE_AVAILABLE:
        try:
            payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate token credential format.",
                headers={"WWW-Authenticate": "Bearer"},
            )
    else:
        # Fallback decode
        if token.startswith("mock_token_"):
            parts = token.split("_")
            return {"sub": parts[2], "role": parts[3] if len(parts) > 3 else "student"}
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token format.",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Security(security)) -> Dict[str, Any]:
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    payload = decode_token(token)
    username = payload.get("sub")
    role = payload.get("role", "student")
    student_id = payload.get("student_id")

    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token payload",
        )

    user = db_manager.get_user_by_username(username)
    if not user:
        # Guest or ephemeral token user
        return {
            "username": username,
            "role": role,
            "student_id": student_id or username
        }

    return {
        "username": user["username"],
        "role": user.get("role", "student"),
        "student_id": user.get("student_id", user["username"]),
        "id": str(user.get("_id", user.get("username")))
    }

def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required for this action."
        )
    return current_user
