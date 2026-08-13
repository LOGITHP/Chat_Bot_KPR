from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.db.mongodb import db
from app.core.permissions import get_current_active_admin
from bson import ObjectId

router = APIRouter()

@router.get("/departments", dependencies=[Depends(get_current_active_admin)])
async def get_departments():
    cursor = db.departments.find({"active": True})
    return [{"id": str(doc["_id"]), **doc} async for doc in cursor]

@router.get("/clubs", dependencies=[Depends(get_current_active_admin)])
async def get_clubs():
    cursor = db.clubs.find({"active": True})
    return [{"id": str(doc["_id"]), **doc} async for doc in cursor]

@router.get("/categories", dependencies=[Depends(get_current_active_admin)])
async def get_categories():
    cursor = db.categories.find({"active": True})
    return [{"id": str(doc["_id"]), **doc} async for doc in cursor]

@router.get("/jobs", dependencies=[Depends(get_current_active_admin)])
async def get_jobs():
    cursor = db.processing_jobs.find().sort("started_at", -1)
    return [{"id": str(doc["_id"]), **doc} async for doc in cursor]
