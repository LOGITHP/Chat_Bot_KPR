import uuid
import os
import tempfile
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks
from app.db.mongodb import db
from app.core.permissions import get_current_active_faculty
from app.rag.ingestion import process_document_background
from app.config import settings

router = APIRouter()

@router.post("/upload", dependencies=[Depends(get_current_active_faculty)])
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    # This is a simplified version. Needs actual MinIO upload.
    # We will simulate MinIO upload by writing to local disk temporarily
    import shutil
    
    file_id = str(uuid.uuid4())
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f"{file_id}_{file.filename}")
    
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    file_size = os.path.getsize(temp_path)
    if file_size == 0:
        raise ValueError("Uploaded file is empty (0 bytes)")
        
    print(f"Uploaded file {file.filename} saved to {temp_path} with size {file_size} bytes")
        
    doc_dict = {
        "title": file.filename,
        "filename": file.filename,
        "object_key": f"documents/{file_id}_{file.filename}",
        "content_type": file.content_type,
        "file_size": file_size,
        "document_type": file.filename.split('.')[-1].lower(),
        "status": "uploaded",
        "active": True,
        "access_level": "public"
    }
    
    result = await db.documents.insert_one(doc_dict)
    doc_id = str(result.inserted_id)
    
    job_dict = {
        "document_id": doc_id,
        "status": "uploaded"
    }
    job_result = await db.processing_jobs.insert_one(job_dict)
    job_id = str(job_result.inserted_id)
    
    background_tasks.add_task(
        process_document_background,
        job_id=job_id,
        document_id=doc_id,
        file_path=temp_path,
        filename=file.filename
    )
    
    return {"message": "Document uploaded and processing started", "document_id": doc_id, "job_id": job_id}
