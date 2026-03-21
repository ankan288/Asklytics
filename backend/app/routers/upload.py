from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.response_models import UploadResponse
from app.services import csv_service

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/csv", response_model=UploadResponse)
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are accepted.")
    content = await file.read()
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 50 MB).")
    try:
        result = await csv_service.process_csv(content, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")
    return UploadResponse(
        datasource_id=result["datasource_id"],
        table_name=result["table_name"],
        columns=result["schema"],
    )
