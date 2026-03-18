"""Supabase Storage service for persistent CSV file uploads"""
import uuid
import io
from typing import Optional, Dict, Any
from supabase import create_client, Client
from app.config import get_settings

def get_supabase_client() -> Client:
    """Get Supabase client for storage operations"""
    settings = get_settings()

    if not settings.supabase_url or not settings.supabase_key:
        raise Exception("Supabase configuration missing")

    return create_client(settings.supabase_url, settings.supabase_key)

async def upload_csv_to_storage(
    file_content: bytes,
    filename: str,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Upload CSV file to Supabase Storage and return file info

    Args:
        file_content: Raw CSV file bytes
        filename: Original filename
        user_id: User ID for file organization (optional for now)

    Returns:
        Dict with file_path, public_url, and metadata
    """
    settings = get_settings()
    supabase = get_supabase_client()

    # Generate unique filename to avoid conflicts
    file_id = str(uuid.uuid4())
    file_extension = filename.split('.')[-1] if '.' in filename else 'csv'
    unique_filename = f"{file_id}.{file_extension}"

    # Add user prefix if user_id provided (for future user-based organization)
    storage_path = f"uploads/{unique_filename}"
    if user_id:
        storage_path = f"users/{user_id}/{unique_filename}"

    try:
        # Upload file to Supabase Storage
        response = supabase.storage.from_(settings.supabase_storage_bucket).upload(
            path=storage_path,
            file=file_content,
            file_options={
                "content-type": "text/csv",
                "cache-control": "3600"
            }
        )

        # Get public URL for the uploaded file
        public_url = supabase.storage.from_(settings.supabase_storage_bucket).get_public_url(storage_path)

        return {
            "file_id": file_id,
            "storage_path": storage_path,
            "public_url": public_url,
            "original_filename": filename,
            "file_size": len(file_content),
            "bucket": settings.supabase_storage_bucket
        }

    except Exception as e:
        raise Exception(f"Failed to upload file to Supabase Storage: {str(e)}")

async def download_csv_from_storage(storage_path: str) -> bytes:
    """
    Download CSV file from Supabase Storage

    Args:
        storage_path: Path to file in storage bucket

    Returns:
        Raw file bytes
    """
    settings = get_settings()
    supabase = get_supabase_client()

    try:
        response = supabase.storage.from_(settings.supabase_storage_bucket).download(storage_path)
        return response
    except Exception as e:
        raise Exception(f"Failed to download file from Supabase Storage: {str(e)}")

async def delete_csv_from_storage(storage_path: str) -> bool:
    """
    Delete CSV file from Supabase Storage

    Args:
        storage_path: Path to file in storage bucket

    Returns:
        True if successful, False otherwise
    """
    settings = get_settings()
    supabase = get_supabase_client()

    try:
        supabase.storage.from_(settings.supabase_storage_bucket).remove([storage_path])
        return True
    except Exception as e:
        print(f"Failed to delete file from Supabase Storage: {str(e)}")
        return False

def list_user_files(user_id: str) -> list:
    """
    List all CSV files for a specific user

    Args:
        user_id: User ID to filter files

    Returns:
        List of file metadata
    """
    settings = get_settings()
    supabase = get_supabase_client()

    try:
        user_folder = f"users/{user_id}/"
        response = supabase.storage.from_(settings.supabase_storage_bucket).list(user_folder)
        return response
    except Exception as e:
        print(f"Failed to list user files: {str(e)}")
        return []