"""CSV upload — parse, type-infer, store in Supabase Storage, register as in-memory SQLite datasource."""
import sqlite3, uuid, io, re, logging
import pandas as pd
from app.database.connection import register_inmemory
from app.services.storage_service import upload_csv_to_storage
from app.config import get_settings

logger = logging.getLogger(__name__)
TABLE_NAME = "uploaded_data"

# Global registry to track file metadata (datasource_id -> file_info)
_file_registry: dict[str, dict] = {}

async def process_csv(file_bytes: bytes, filename: str, user_id: str = None) -> dict:
    """
    Process CSV file: store in Supabase Storage + create in-memory database for fast queries

    Args:
        file_bytes: Raw CSV content
        filename: Original filename
        user_id: User ID (optional, for future user-based file organization)

    Returns:
        Dict with datasource_id, table_name, schema, and file info
    """
    settings = get_settings()
    datasource_id = str(uuid.uuid4())

    try:
        # Decode file content
        try:
            text = file_bytes.decode("utf-8", errors="replace")
        except Exception:
            text = file_bytes.decode("latin-1", errors="replace")

        # Strip HTML web-archive wrapper if present
        if "<pre" in text[:2000]:
            m = re.search(r"<pre[^>]*>(.*?)</pre>", text, re.DOTALL | re.IGNORECASE)
            if m:
                text = m.group(1).strip()

        # Parse CSV with pandas
        df = pd.read_csv(io.StringIO(text))
        if df.empty:
            raise ValueError("The uploaded CSV file is empty.")

        # Sanitise column names
        df.columns = [re.sub(r"[^a-zA-Z0-9_]", "_", c.strip().lower()) for c in df.columns]

        # Create in-memory SQLite database for fast queries
        conn = sqlite3.connect(":memory:", check_same_thread=False)
        conn.row_factory = sqlite3.Row
        df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
        conn.commit()

        # Register in-memory database for queries
        register_inmemory(datasource_id, conn)

        # Store file in Supabase Storage for persistence (production)
        file_info = None
        if settings.environment == "production" and settings.supabase_url:
            try:
                file_info = await upload_csv_to_storage(file_bytes, filename, user_id)
                logger.info(f"✅ File stored in Supabase Storage: {file_info['storage_path']}")
            except Exception as e:
                logger.warning(f"⚠️ Supabase Storage failed, using in-memory only: {e}")
        else:
            logger.info("🔧 Development mode: using in-memory storage only")

        # Store file metadata in registry
        _file_registry[datasource_id] = {
            "original_filename": filename,
            "file_size": len(file_bytes),
            "row_count": len(df),
            "columns": list(df.columns),
            "created_at": pd.Timestamp.now().isoformat(),
            "storage_info": file_info,  # None in development, file info in production
            "user_id": user_id
        }

        schema = {col: str(dtype) for col, dtype in zip(df.columns, df.dtypes)}
        logger.info(f"CSV '{filename}' → datasource {datasource_id} ({len(df):,} rows)")

        return {
            "datasource_id": datasource_id,
            "table_name": TABLE_NAME,
            "schema": schema,
            "row_count": len(df),
            "file_info": _file_registry[datasource_id]
        }

    except Exception as e:
        logger.error(f"❌ CSV processing failed: {e}")
        raise ValueError(f"Failed to process CSV: {str(e)}")

def get_file_info(datasource_id: str) -> dict:
    """Get file metadata for a datasource"""
    return _file_registry.get(datasource_id, {})

def list_uploaded_files() -> list:
    """List all uploaded files with metadata"""
    return [
        {
            "datasource_id": ds_id,
            **file_info
        }
        for ds_id, file_info in _file_registry.items()
    ]

async def cleanup_datasource(datasource_id: str) -> bool:
    """
    Clean up datasource: remove from memory and delete from storage

    Args:
        datasource_id: Datasource to clean up

    Returns:
        True if successful, False otherwise
    """
    success = True

    # Remove from file registry
    file_info = _file_registry.pop(datasource_id, {})

    # Clean up Supabase Storage (production only)
    if file_info.get("storage_info") and file_info["storage_info"].get("storage_path"):
        try:
            from app.services.storage_service import delete_csv_from_storage
            await delete_csv_from_storage(file_info["storage_info"]["storage_path"])
            logger.info(f"✅ File deleted from Supabase Storage: {file_info['storage_info']['storage_path']}")
        except Exception as e:
            logger.error(f"❌ Failed to delete from storage: {e}")
            success = False

    return success
