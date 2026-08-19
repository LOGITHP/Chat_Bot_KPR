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


# ─── Content management & CRUD ────────────────────────────

@router.get("/stats", dependencies=[Depends(get_current_active_admin)])
async def get_dashboard_stats():
    total_users = await db.users.count_documents({})
    total_students = await db.users.count_documents({"role": "student"})
    total_faculty = await db.users.count_documents({"role": "faculty"})
    total_docs = await db.documents.count_documents({})
    total_departments = await db.departments.count_documents({"active": True})
    total_clubs = await db.clubs.count_documents({"active": True})
    total_transport = await db.transport.count_documents({"active": True})
    
    recent_jobs_cursor = db.processing_jobs.find().sort("started_at", -1).limit(6)
    recent_jobs = [{"id": str(doc["_id"]), **{k: v for k, v in doc.items() if k != "_id"}} async for doc in recent_jobs_cursor]
    
    return {
        "users": {
            "total": total_users,
            "students": total_students,
            "faculty": total_faculty
        },
        "documents": {
            "total": total_docs
        },
        "content": {
            "departments": total_departments,
            "clubs": total_clubs,
            "transport": total_transport
        },
        "recent_jobs": recent_jobs
    }

# ─── Documents Management ────────────────────────────

@router.get("/documents", dependencies=[Depends(get_current_active_admin)])
async def get_all_documents():
    cursor = db.documents.find().sort("created_at", -1)
    return [{"id": str(doc["_id"]), **{k: v for k, v in doc.items() if k != "_id"}} async for doc in cursor]

@router.delete("/documents/{doc_id}", dependencies=[Depends(get_current_active_admin)])
async def delete_document(doc_id: str):
    from app.vector.qdrant_client import qdrant_client
    try:
        qdrant_client.delete_by_document_id(doc_id)
    except Exception as e:
        print(f"[Warning] Failed to remove vector points for {doc_id}: {e}")
        
    res = await db.documents.delete_one({"_id": ObjectId(doc_id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    await db.processing_jobs.delete_many({"document_id": doc_id})
    return {"message": "Document deleted successfully"}

# ─── Departments ────────────────────────────────────

@router.get("/departments", dependencies=[Depends(get_current_active_admin)])
async def get_departments():
    cursor = db.departments.find().sort("name", 1)
    return [{"id": str(doc["_id"]), **{k: v for k, v in doc.items() if k != "_id"}} async for doc in cursor]

@router.post("/departments", dependencies=[Depends(get_current_active_admin)])
async def create_department(data: dict):
    doc = {
        "code": data.get("code", "").upper(),
        "name": data.get("name", ""),
        "hod": data.get("hod", ""),
        "location": data.get("location", ""),
        "description": data.get("description", ""),
        "active": data.get("active", True),
        "created_at": datetime.utcnow()
    }
    res = await db.departments.insert_one(doc)
    return {"id": str(res.inserted_id), "message": "Department created"}

@router.patch("/departments/{dept_id}", dependencies=[Depends(get_current_active_admin)])
async def update_department(dept_id: str, data: dict):
    update_data = {k: v for k, v in data.items() if k != "id" and k != "_id"}
    update_data["updated_at"] = datetime.utcnow()
    res = await db.departments.update_one({"_id": ObjectId(dept_id)}, {"$set": update_data})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Department not found")
    return {"message": "Department updated"}

@router.delete("/departments/{dept_id}", dependencies=[Depends(get_current_active_admin)])
async def delete_department(dept_id: str):
    res = await db.departments.delete_one({"_id": ObjectId(dept_id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Department not found")
    return {"message": "Department deleted"}

# ─── Clubs ──────────────────────────────────────────

@router.get("/clubs", dependencies=[Depends(get_current_active_admin)])
async def get_clubs():
    cursor = db.clubs.find().sort("name", 1)
    return [{"id": str(doc["_id"]), **{k: v for k, v in doc.items() if k != "_id"}} async for doc in cursor]

@router.post("/clubs", dependencies=[Depends(get_current_active_admin)])
async def create_club(data: dict):
    doc = {
        "name": data.get("name", ""),
        "category": data.get("category", "Technical"),
        "faculty_incharge": data.get("faculty_incharge", ""),
        "student_lead": data.get("student_lead", ""),
        "description": data.get("description", ""),
        "active": data.get("active", True),
        "created_at": datetime.utcnow()
    }
    res = await db.clubs.insert_one(doc)
    return {"id": str(res.inserted_id), "message": "Club created"}

@router.patch("/clubs/{club_id}", dependencies=[Depends(get_current_active_admin)])
async def update_club(club_id: str, data: dict):
    update_data = {k: v for k, v in data.items() if k != "id" and k != "_id"}
    update_data["updated_at"] = datetime.utcnow()
    res = await db.clubs.update_one({"_id": ObjectId(club_id)}, {"$set": update_data})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Club not found")
    return {"message": "Club updated"}

@router.delete("/clubs/{club_id}", dependencies=[Depends(get_current_active_admin)])
async def delete_club(club_id: str):
    res = await db.clubs.delete_one({"_id": ObjectId(club_id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Club not found")
    return {"message": "Club deleted"}

# ─── Categories ─────────────────────────────────────

@router.get("/categories", dependencies=[Depends(get_current_active_admin)])
async def get_categories():
    cursor = db.categories.find().sort("name", 1)
    return [{"id": str(doc["_id"]), **{k: v for k, v in doc.items() if k != "_id"}} async for doc in cursor]

@router.post("/categories", dependencies=[Depends(get_current_active_admin)])
async def create_category(data: dict):
    doc = {
        "name": data.get("name", ""),
        "slug": data.get("slug", "").lower().replace(" ", "-"),
        "description": data.get("description", ""),
        "icon": data.get("icon", "Folder"),
        "active": data.get("active", True),
        "created_at": datetime.utcnow()
    }
    res = await db.categories.insert_one(doc)
    return {"id": str(res.inserted_id), "message": "Category created"}

@router.patch("/categories/{cat_id}", dependencies=[Depends(get_current_active_admin)])
async def update_category(cat_id: str, data: dict):
    update_data = {k: v for k, v in data.items() if k != "id" and k != "_id"}
    update_data["updated_at"] = datetime.utcnow()
    res = await db.categories.update_one({"_id": ObjectId(cat_id)}, {"$set": update_data})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category updated"}

@router.delete("/categories/{cat_id}", dependencies=[Depends(get_current_active_admin)])
async def delete_category(cat_id: str):
    res = await db.categories.delete_one({"_id": ObjectId(cat_id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted"}

# ─── Transport ──────────────────────────────────────

@router.get("/transport", dependencies=[Depends(get_current_active_admin)])
async def get_transport_routes():
    cursor = db.transport.find().sort("route_number", 1)
    return [{"id": str(doc["_id"]), **{k: v for k, v in doc.items() if k != "_id"}} async for doc in cursor]

@router.post("/transport", dependencies=[Depends(get_current_active_admin)])
async def create_transport_route(data: dict):
    doc = {
        "route_number": data.get("route_number", ""),
        "destination": data.get("destination", ""),
        "driver_name": data.get("driver_name", ""),
        "driver_contact": data.get("driver_contact", ""),
        "departure_time": data.get("departure_time", "07:30 AM"),
        "stops": data.get("stops", []),
        "active": data.get("active", True),
        "created_at": datetime.utcnow()
    }
    res = await db.transport.insert_one(doc)
    return {"id": str(res.inserted_id), "message": "Transport route created"}

@router.patch("/transport/{route_id}", dependencies=[Depends(get_current_active_admin)])
async def update_transport_route(route_id: str, data: dict):
    update_data = {k: v for k, v in data.items() if k != "id" and k != "_id"}
    update_data["updated_at"] = datetime.utcnow()
    res = await db.transport.update_one({"_id": ObjectId(route_id)}, {"$set": update_data})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Route not found")
    return {"message": "Transport route updated"}

@router.delete("/transport/{route_id}", dependencies=[Depends(get_current_active_admin)])
async def delete_transport_route(route_id: str):
    res = await db.transport.delete_one({"_id": ObjectId(route_id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Route not found")
    return {"message": "Transport route deleted"}

# ─── Campus Data ────────────────────────────────────

@router.get("/campus-data", dependencies=[Depends(get_current_active_admin)])
async def get_campus_data():
    cursor = db.campus_data.find().sort("title", 1)
    return [{"id": str(doc["_id"]), **{k: v for k, v in doc.items() if k != "_id"}} async for doc in cursor]

@router.post("/campus-data", dependencies=[Depends(get_current_active_admin)])
async def create_campus_data(data: dict):
    doc = {
        "title": data.get("title", ""),
        "category": data.get("category", "General"),
        "content": data.get("content", ""),
        "tags": data.get("tags", []),
        "active": data.get("active", True),
        "created_at": datetime.utcnow()
    }
    res = await db.campus_data.insert_one(doc)
    return {"id": str(res.inserted_id), "message": "Campus data added"}

@router.patch("/campus-data/{item_id}", dependencies=[Depends(get_current_active_admin)])
async def update_campus_data(item_id: str, data: dict):
    update_data = {k: v for k, v in data.items() if k != "id" and k != "_id"}
    update_data["updated_at"] = datetime.utcnow()
    res = await db.campus_data.update_one({"_id": ObjectId(item_id)}, {"$set": update_data})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Campus data updated"}

@router.delete("/campus-data/{item_id}", dependencies=[Depends(get_current_active_admin)])
async def delete_campus_data(item_id: str):
    res = await db.campus_data.delete_one({"_id": ObjectId(item_id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Campus data deleted"}

# ─── Processing Jobs ────────────────────────────────

@router.get("/jobs", dependencies=[Depends(get_current_active_admin)])
async def get_jobs():
    cursor = db.processing_jobs.find().sort("started_at", -1).limit(50)
    return [{"id": str(doc["_id"]), **{k: v for k, v in doc.items() if k != "_id"}} async for doc in cursor]

