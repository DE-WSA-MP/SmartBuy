
from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.scrapers.base import standardize_store_data, REQUIRED_COLUMNS


def test_standardize_store_data():
    records = [
        {
            "product_id": "A101",
            "store": "Incorrect Name",
            "product_name": "Samsung Galaxy S25",
            "brand": "Samsung",
            "model": "Galaxy S25",
            "price": 74999,
            "rating": 4.5,
            "review_count": 2341,
            "availability": "In Stock",
            "product_url": "http://store-a.local/products/galaxy-s25",
        }
    ]

    result = standardize_store_data(records, "Store A")

    assert list(result.columns) == REQUIRED_COLUMNS
    assert len(result) == 1
    assert result.iloc[0]["store"] == "Store A"
    assert result.iloc[0]["price"] == 74999

    print("Scraper interface test passed!")


if __name__ == "__main__":
    test_standardize_store_data()
