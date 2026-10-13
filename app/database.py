
import sqlite3
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "data" / "smartbuy.db"
SAMPLE_DATA_PATH = PROJECT_ROOT / "data" / "sample_products.csv"


def get_connection():
    """Create a connection to the SmartBuy SQLite database."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DATABASE_PATH)


def initialize_database():
    """Create the products table if it does not exist."""

    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id TEXT PRIMARY KEY,
                store TEXT NOT NULL,
                product_name TEXT NOT NULL,
                brand TEXT NOT NULL,
                model TEXT NOT NULL,
                price REAL NOT NULL,
                rating REAL NOT NULL,
                review_count INTEGER NOT NULL,
                availability TEXT NOT NULL,
                product_url TEXT NOT NULL
            )
        """)


def save_products(products):
    """Insert or update validated product records."""

    columns = [
        "product_id",
        "store",
        "product_name",
        "brand",
        "model",
        "price",
        "rating",
        "review_count",
        "availability",
        "product_url",
    ]

    missing = set(columns) - set(products.columns)

    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    records = products[columns].copy()

    # Convert pandas missing values to Python None for SQLite.
    records = records.astype(object).where(
        pd.notna(records), None
    )

    rows = list(records.itertuples(index=False, name=None))

    with get_connection() as connection:
        connection.executemany("""
            INSERT INTO products (
                product_id, store, product_name, brand, model,
                price, rating, review_count, availability, product_url
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(product_id) DO UPDATE SET
                store = excluded.store,
                product_name = excluded.product_name,
                brand = excluded.brand,
                model = excluded.model,
                price = excluded.price,
                rating = excluded.rating,
                review_count = excluded.review_count,
                availability = excluded.availability,
                product_url = excluded.product_url
        """, rows)


def load_products():
    """Load all stored product records into a DataFrame."""

    with get_connection() as connection:
        return pd.read_sql_query(
            "SELECT * FROM products ORDER BY store, product_id",
            connection,
        )


def seed_sample_data():
    """
    Initialize the database and load sample data only when
    the products table is empty.
    """

    initialize_database()

    existing = load_products()

    if not existing.empty:
        return

    if not SAMPLE_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Sample data not found: {SAMPLE_DATA_PATH}"
        )

    sample_products = pd.read_csv(SAMPLE_DATA_PATH)
    save_products(sample_products)


if __name__ == "__main__":
    seed_sample_data()
    products = load_products()

    print("Database:", DATABASE_PATH)
    print("Stored product records:", len(products))
    print(products[["store", "product_name", "price"]].to_string(index=False))
