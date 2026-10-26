"""Script to generate a rich, reproducible sample Amazon Sales dataset (200 rows) for testing and out-of-the-box local development."""

import csv
import random
from datetime import datetime, timedelta

CATEGORIES = {
    "Electronics": (80.0, 800.0, ["Headphones", "Smartphone", "Smartwatch", "Laptop Sleeve", "Bluetooth Speaker"]),
    "Fashion": (20.0, 150.0, ["T-Shirt", "Jeans", "Jacket", "Sneakers", "Dress"]),
    "Home & Kitchen": (25.0, 300.0, ["Coffee Maker", "Blender", "Air Fryer", "Toaster", "Cookware Set"]),
    "Books": (10.0, 45.0, ["Data Science Handbook", "Novel", "Finance Guide", "Cookbook", "History of AI"]),
    "Beauty": (15.0, 90.0, ["Serum", "Moisturizer", "Lipstick", "Perfume", "Face Cleanser"]),
    "Sports": (20.0, 200.0, ["Yoga Mat", "Dumbbells", "Running Shoes", "Water Bottle", "Tennis Racket"]),
}

REGIONS = ["North America", "Europe", "Asia", "Latin America"]
PAYMENTS = ["Credit Card", "PayPal", "Debit Card", "UPI", "Net Banking"]

random.seed(42)
start_date = datetime(2022, 1, 1)

rows = []
for i in range(1, 201):
    order_id = 1000 + i
    dt = start_date + timedelta(days=random.randint(0, 720))
    order_date = dt.strftime("%Y-%m-%d")
    product_id = 5000 + random.randint(1, 50)
    category = random.choice(list(CATEGORIES.keys()))
    min_p, max_p, _ = CATEGORIES[category]
    price = round(random.uniform(min_p, max_p), 2)
    discount_pct = random.choice([0, 5, 10, 15, 20, 25, 30])
    qty = random.randint(1, 5)
    region = random.choice(REGIONS)
    payment = random.choice(PAYMENTS)
    rating = round(random.uniform(3.5, 5.0), 1)
    review_count = random.randint(10, 850)
    discounted_price = round(price * (1 - discount_pct / 100.0), 2)
    total_revenue = round(discounted_price * qty, 2)

    rows.append({
        "order_id": order_id,
        "order_date": order_date,
        "product_id": product_id,
        "product_category": category,
        "price": price,
        "discount_percent": discount_pct,
        "quantity_sold": qty,
        "customer_region": region,
        "payment_method": payment,
        "rating": rating,
        "review_count": review_count,
        "discounted_price": discounted_price,
        "total_revenue": total_revenue,
    })

with open("data/amazon_sales_sample.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

print(f"Generated data/amazon_sales_sample.csv with {len(rows)} records.")
