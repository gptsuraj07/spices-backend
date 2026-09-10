from fastapi import APIRouter, File, UploadFile, HTTPException
import shutil
import os
import uuid

router = APIRouter(prefix="/api/upload", tags=["Upload"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("", response_model=dict)
async def upload_file(file: UploadFile = File(...)):
    try:
        filename_parts = file.filename.split(".")
        ext = filename_parts[-1] if len(filename_parts) > 1 else "jpg"
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        target_path = os.path.join(UPLOAD_DIR, unique_filename)

        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Return relative URL and full URL
        url = f"/uploads/{unique_filename}"
        return {
            "url": url,
            "filename": unique_filename,
            "message": "File uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")
