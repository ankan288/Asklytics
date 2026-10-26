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
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    raw_candidates = [
        s.sample_csv_path,
        os.path.join(repo_root, "data", "amazon_sales_sample.csv"),
        os.path.join(backend_root, "data", "amazon_sales.csv"),
        os.path.join(repo_root, "7. Amazon Sales", "Amazon Sales.csv"),
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
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
    if cur.fetchone()[0] == 0:
        sample_rows = [
            (1001, '2023-01-15', 501, 'Electronics', 299.99, 10, 2, 'North America', 'Credit Card', 4.7, 120, 269.99, 539.98),
            (1002, '2023-01-18', 502, 'Electronics', 149.99, 5, 1, 'Europe', 'PayPal', 4.5, 85, 142.49, 142.49),
            (1003, '2023-02-01', 503, 'Fashion', 79.99, 20, 3, 'Asia', 'Credit Card', 4.2, 210, 63.99, 191.97),
            (1004, '2023-02-14', 504, 'Fashion', 49.99, 15, 2, 'North America', 'Debit Card', 4.0, 95, 42.49, 84.98),
            (1005, '2023-03-05', 505, 'Home & Kitchen', 129.99, 0, 1, 'Europe', 'Credit Card', 4.8, 310, 129.99, 129.99),
            (1006, '2023-03-22', 506, 'Books', 19.99, 10, 4, 'North America', 'PayPal', 4.9, 540, 17.99, 71.96),
            (1007, '2023-04-10', 507, 'Beauty', 34.99, 5, 2, 'Asia', 'Credit Card', 4.3, 160, 33.24, 66.48),
            (1008, '2023-04-28', 508, 'Sports', 89.99, 25, 1, 'Europe', 'Credit Card', 4.6, 75, 67.49, 67.49),
            (1009, '2023-05-12', 509, 'Electronics', 499.99, 10, 1, 'North America', 'Credit Card', 4.8, 420, 449.99, 449.99),
            (1010, '2023-05-25', 510, 'Books', 24.99, 0, 2, 'Asia', 'Debit Card', 4.4, 88, 24.99, 49.98),
        ]
        conn.executemany(
            f"INSERT INTO {TABLE_NAME} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            sample_rows,
        )
        conn.commit()
        logger.info(f"Seeded {len(sample_rows)} default fallback rows into '{TABLE_NAME}'.")
    else:
        conn.commit()
