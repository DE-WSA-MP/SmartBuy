
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.scrapers.runner import run_scrapers


def store_a_scraper():
    return [
        {
            "product_id": "A101",
            "store": "Store A",
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


def store_b_scraper():
    return [
        {
            "product_id": "B201",
            "store": "Store B",
            "product_name": "Samsung Galaxy S25 5G",
            "brand": "Samsung",
            "model": "Galaxy S25",
            "price": 72999,
            "rating": 4.4,
            "review_count": 1800,
            "availability": "In Stock",
            "product_url": "http://store-b.local/products/galaxy-s25",
        }
    ]


def failing_store_scraper():
    raise ConnectionError("Simulated store connection failure")


def test_scraper_runner():
    scrapers = {
        "Store A": store_a_scraper,
        "Store B": store_b_scraper,
        "Store C": failing_store_scraper,
    }

    products, status = run_scrapers(scrapers)

    assert len(products) == 2
    assert products["store"].tolist() == ["Store A", "Store B"]

    assert status["Store A"]["success"] is True
    assert status["Store A"]["records_found"] == 1

    assert status["Store B"]["success"] is True
    assert status["Store B"]["records_found"] == 1

    assert status["Store C"]["success"] is False
    assert "Simulated store connection failure" in status["Store C"]["error"]

    print("Combined products:", len(products))
    print("Store status:")

    for store, details in status.items():
        print(
            f"{store}: success={details['success']}, "
            f"records={details['records_found']}, "
            f"error={details['error']}"
        )

    print("All scraper runner tests passed!")


if __name__ == "__main__":
    test_scraper_runner()
