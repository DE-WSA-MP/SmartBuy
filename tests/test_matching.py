
from pathlib import Path
import sys
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.processing import clean_and_validate_products
from app.matching import match_products


def main():
    data_file = PROJECT_ROOT / "data" / "sample_products.csv"

    raw_data = pd.read_csv(data_file)
    cleaned_data, rejected_data = clean_and_validate_products(raw_data)

    matched_data = match_products(cleaned_data)

    print("\n--- PRODUCT MATCHING RESULTS ---")

    for group_id, group in matched_data.groupby(
        "product_group", dropna=False
    ):
        print(f"\nProduct group: {group_id}")

        for _, product in group.iterrows():
            print(
                f"{product['store']}: "
                f"{product['product_name']} | "
                f"₹{product['price']}"
            )

    print("\n--- SUMMARY ---")
    print(f"Valid records: {len(cleaned_data)}")
    print(f"Rejected records: {len(rejected_data)}")
    print(
        "Matched product groups:",
        matched_data["product_group"].nunique()
    )


if __name__ == "__main__":
    main()
