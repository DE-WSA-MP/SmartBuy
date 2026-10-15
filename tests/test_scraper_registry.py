
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.scrapers.registry import (
    register_scraper,
    get_registered_scrapers,
    collect_from_registered_stores,
)


def test_registry():
    def fake_store_scraper():
        return [
            {
                "product_id": "TEST001",
                "store": "Temporary",
                "product_name": "Test Phone",
                "brand": "TestBrand",
                "model": "TestPhone1",
                "price": 10000,
                "rating": 4.2,
                "review_count": 100,
                "availability": "In Stock",
                "product_url": "http://127.0.0.1:5001/products/test-phone",
            }
        ]

    register_scraper("Test Store", fake_store_scraper)

    registered = get_registered_scrapers()
    assert "Test Store" in registered

    products, status = collect_from_registered_stores()

    assert len(products) == 1
    assert status["Test Store"]["success"] is True
    assert status["Test Store"]["records_found"] == 1

    print("Registered stores:", list(registered.keys()))
    print("Products collected:", len(products))
    print("Registry test passed!")


if __name__ == "__main__":
    test_registry()
