from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.db.mongodb import db
from app.core.permissions import get_current_active_admin
from app.core.security import get_password_hash, create_access_token
from datetime import timedelta

router = APIRouter()

# ─── User Management ───────────────────────────────────────────

class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str = "student"           # student | faculty | admin
    student_id: Optional[str] = None
    department_id: Optional[str] = None
    year: Optional[int] = None
    section: Optional[str] = None

class UpdateUserRequest(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    department_id: Optional[str] = None
    year: Optional[int] = None
    section: Optional[str] = None
    active: Optional[bool] = None

class AdminResetPasswordRequest(BaseModel):
    new_password: str

def serialize_user(u: dict) -> dict:
    u = dict(u)
    u["id"] = str(u.pop("_id"))
    u.pop("password_hash", None)
    return u


@router.get("/users", dependencies=[Depends(get_current_active_admin)])
async def list_users(role: Optional[str] = None, active: Optional[bool] = None):
    query = {}
    if role:
        query["role"] = role
    if active is not None:
        query["active"] = active
    cursor = db.users.find(query).sort("created_at", -1)
    users = await cursor.to_list(length=500)
    return [serialize_user(u) for u in users]


@router.post("/users", dependencies=[Depends(get_current_active_admin)])
async def create_user(body: CreateUserRequest):
    existing = await db.users.find_one({"email": body.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered.")

    if body.student_id:
        dup = await db.users.find_one({"student_id": body.student_id})
        if dup:
            raise HTTPException(status_code=400, detail="Student ID already registered.")

    user_doc = {
        "email":         body.email,
        "password_hash": get_password_hash(body.password),
        "name":          body.name,
        "role":          body.role,
        "student_id":    body.student_id,
        "department_id": body.department_id,
        "year":          body.year,
        "section":       body.section,
        "club_ids":      [],
        "active":        True,
        "created_at":    datetime.utcnow(),
        "updated_at":    datetime.utcnow(),
    }
    result = await db.users.insert_one(user_doc)
    return {"message": "User created successfully.", "id": str(result.inserted_id)}


@router.patch("/users/{user_id}", dependencies=[Depends(get_current_active_admin)])
async def update_user(user_id: str, body: UpdateUserRequest):
    update_data = {k: v for k, v in body.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update.")
    update_data["updated_at"] = datetime.utcnow()
    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"message": "User updated."}


@router.delete("/users/{user_id}", dependencies=[Depends(get_current_active_admin)])
async def deactivate_user(user_id: str):
    """Soft-delete: set active=False."""
    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"active": False, "updated_at": datetime.utcnow()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"message": "User deactivated."}


@router.post("/users/{user_id}/reset-password", dependencies=[Depends(get_current_active_admin)])
async def admin_reset_password(user_id: str, body: AdminResetPasswordRequest):
    new_hash = get_password_hash(body.new_password)
    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"password_hash": new_hash, "updated_at": datetime.utcnow()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found.")
    # Revoke sessions
    await db.sessions.delete_many({"user_id": user_id})
    return {"message": "Password reset successfully."}


@router.post("/users/{user_id}/generate-reset-link", dependencies=[Depends(get_current_active_admin)])
async def generate_reset_link_for_user(user_id: str):
    """Admin generates a reset token they can share with a student."""
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    token = create_access_token(subject=user_id, expires_delta=timedelta(minutes=60))
    await db.password_reset_tokens.insert_one({
        "user_id":    user_id,
        "token":      token,
        "used":       False,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(minutes=60),
    })
    return {"reset_token": token, "expires_in_minutes": 60}


# ─── Content management (existing) ────────────────────────────

@router.get("/departments", dependencies=[Depends(get_current_active_admin)])
async def get_departments():
    cursor = db.departments.find({"active": True})
    return [{"id": str(doc["_id"]), **{k: v for k, v in doc.items() if k != "_id"}} async for doc in cursor]

@router.get("/clubs", dependencies=[Depends(get_current_active_admin)])
async def get_clubs():
    cursor = db.clubs.find({"active": True})
    return [{"id": str(doc["_id"]), **{k: v for k, v in doc.items() if k != "_id"}} async for doc in cursor]

@router.get("/categories", dependencies=[Depends(get_current_active_admin)])
async def get_categories():
    cursor = db.categories.find({"active": True})
    return [{"id": str(doc["_id"]), **{k: v for k, v in doc.items() if k != "_id"}} async for doc in cursor]

@router.get("/jobs", dependencies=[Depends(get_current_active_admin)])
async def get_jobs():
    cursor = db.processing_jobs.find().sort("started_at", -1)
    return [{"id": str(doc["_id"]), **{k: v for k, v in doc.items() if k != "_id"}} async for doc in cursor]
