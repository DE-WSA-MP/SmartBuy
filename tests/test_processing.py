
from pathlib import Path
import sys
import pandas as pd

# Add the project root to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.processing import clean_and_validate_products

DATA_FILE = PROJECT_ROOT / "data" / "sample_products.csv"



def main():
    products = pd.read_csv(DATA_FILE)

    cleaned, rejected = clean_and_validate_products(products)

    print("\n--- CLEANED PRODUCT DATA ---")
    print(cleaned.to_string(index=False))

    print("\n--- REJECTED PRODUCT DATA ---")
    if rejected.empty:
        print("No rejected records.")
    else:
        print(rejected.to_string(index=False))

    print("\n--- SUMMARY ---")
    print(f"Original records: {len(products)}")
    print(f"Valid records: {len(cleaned)}")
    print(f"Rejected records: {len(rejected)}")


if __name__ == "__main__":
    main()
