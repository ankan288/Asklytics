"""Seed the default SQLite database from the Amazon Sales CSV on startup."""
import sqlite3, os, re, io, logging
from app.config import get_settings

logger = logging.getLogger(__name__)
TABLE_NAME = "amazon_sales"


def _expand_csv_candidate(path: str) -> list[str]:
    if not path:
        return []

    cleaned = path.strip().strip('"').strip("'")
    expanded = os.path.expandvars(os.path.expanduser(cleaned))
    candidates = [expanded]

    # Accept either a direct CSV path or a directory containing the CSV.
    if os.path.isdir(expanded):
        candidates.extend([
            os.path.join(expanded, "Amazon Sales.csv"),
            os.path.join(expanded, "amazon_sales.csv"),
        ])

    return candidates


def _find_csv() -> str:
    s = get_settings()
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    raw_candidates = [
        s.sample_csv_path,
        os.path.join(project_root, "7. Amazon Sales", "Amazon Sales.csv"),
        os.path.join(project_root, "7. Amazon Sales"),
        os.path.join(backend_root, "data", "amazon_sales.csv"),
    ]

    for raw in raw_candidates:
        for candidate in _expand_csv_candidate(raw):
            if os.path.isfile(candidate):
                return candidate

    raise FileNotFoundError(
        "Amazon Sales CSV not found. Set SAMPLE_CSV_PATH in .env to the CSV file path "
        "or the folder that contains it."
    )


def _read_csv(path: str) -> str:
    with open(path, "rb") as f:
        raw = f.read()
    try:
        text = raw.decode("utf-8", errors="replace")
    except Exception:
        text = raw.decode("latin-1", errors="replace")
    # Strip HTML web-archive wrapper if present
    if "<pre" in text[:2000]:
        m = re.search(r"<pre[^>]*>(.*?)</pre>", text, re.DOTALL | re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return text


def seed_database(db_path: str) -> None:
    import pandas as pd
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (TABLE_NAME,))
    if cur.fetchone():
        logger.info("DB already seeded — skipping.")
        conn.close()
        return
    try:
        path = _find_csv()
        logger.info(f"Seeding from: {path}")
        text = _read_csv(path)
        df = pd.read_csv(io.StringIO(text))
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
        df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
        conn.commit()
        logger.info(f"Seeded {len(df):,} rows into '{TABLE_NAME}'")
    except FileNotFoundError as e:
        logger.warning(str(e))
        _create_empty(conn)
    except Exception as e:
        logger.error(f"Seed failed: {e}")
        _create_empty(conn)
    finally:
        conn.close()


def _create_empty(conn: sqlite3.Connection) -> None:
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            order_id INTEGER, order_date TEXT, product_id INTEGER,
            product_category TEXT, price REAL, discount_percent INTEGER,
            quantity_sold INTEGER, customer_region TEXT, payment_method TEXT,
            rating REAL, review_count INTEGER, discounted_price REAL, total_revenue REAL
        )
    """)
    conn.commit()
    logger.warning("Created empty fallback table.")
