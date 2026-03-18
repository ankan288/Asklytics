"""CSV upload — parse, type-infer, register as in-memory SQLite datasource."""
import sqlite3, uuid, io, re, logging
import pandas as pd
from app.database.connection import register_inmemory

logger = logging.getLogger(__name__)
TABLE_NAME = "uploaded_data"


def process_csv(file_bytes: bytes, filename: str) -> dict:
    try:
        text = file_bytes.decode("utf-8", errors="replace")
    except Exception:
        text = file_bytes.decode("latin-1", errors="replace")

    # Strip HTML web-archive wrapper if present
    if "<pre" in text[:2000]:
        m = re.search(r"<pre[^>]*>(.*?)</pre>", text, re.DOTALL | re.IGNORECASE)
        if m:
            text = m.group(1).strip()

    df = pd.read_csv(io.StringIO(text))
    if df.empty:
        raise ValueError("The uploaded CSV file is empty.")

    # Sanitise column names
    df.columns = [re.sub(r"[^a-zA-Z0-9_]", "_", c.strip().lower()) for c in df.columns]

    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
    conn.commit()

    datasource_id = str(uuid.uuid4())
    register_inmemory(datasource_id, conn)

    schema = {col: str(dtype) for col, dtype in zip(df.columns, df.dtypes)}
    logger.info(f"CSV '{filename}' → datasource {datasource_id} ({len(df):,} rows)")
    return {"datasource_id": datasource_id, "table_name": TABLE_NAME, "schema": schema, "row_count": len(df)}
