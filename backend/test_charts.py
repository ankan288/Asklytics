import sys
import os

# Ensure the app imports work properly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.gemini_service import generate_dashboard
from app.config import get_settings

schema = """
TABLE amazon_sales(
  order_id TEXT,
  product_category TEXT,
  price REAL,
  rating REAL,
  region TEXT,
  month TEXT
)
"""

print("Testing Scatter Plot...")
res_scatter = generate_dashboard(schema, "Show me the correlation between price and rating", [])
print("SCATTER RESULT:", res_scatter)

print("\nTesting Heatmap...")
res_heatmap = generate_dashboard(schema, "Show me the distribution density of orders by region and product category", [])
print("HEATMAP RESULT:", res_heatmap)
