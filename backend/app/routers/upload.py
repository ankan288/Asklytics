import os
import re
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.response_models import UploadResponse
from app.services import csv_service
from app.services.security import sanitize_error_message

router = APIRouter(prefix="/upload", tags=["upload"])

MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 Megabytes


@router.post("/csv", response_model=UploadResponse)
async def upload_csv(file: UploadFile = File(...)):
    # 1. Filename validation
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing file name.")

    # Guard against directory traversal
    base_name = os.path.basename(file.filename)
    if ".." in base_name or "/" in base_name or "\\" in base_name:
        raise HTTPException(status_code=400, detail="Invalid filename format.")

    if not base_name.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only standard .csv files are supported.")

    # 2. Content-Type validation
    if file.content_type and not any(t in file.content_type.lower() for t in ["csv", "text/plain", "octet-stream", "excel"]):
        raise HTTPException(status_code=400, detail="MIME type rejected. Expected text/csv format.")

    # 3. Read and check size
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large. Maximum supported size is {MAX_FILE_SIZE // (1024 * 1024)} MB.")

    # 4. Check for null bytes / binary file disguised as CSV
    sample = content[:1024]
    if b"\x00" in sample:
        raise HTTPException(status_code=400, detail="Corrupted file format: Binary characters detected in CSV text.")

    # 5. Process CSV with sanitized error capture
    try:
        result = await csv_service.process_csv(content, base_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=sanitize_error_message(str(e)))
    except Exception as e:
        raise HTTPException(status_code=500, detail=sanitize_error_message("CSV parsing and ingestion failed."))

    return UploadResponse(
        datasource_id=result["datasource_id"],
        table_name=result["table_name"],
        columns=result["schema"],
    )
