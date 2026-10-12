
from pathlib import Path
import sys
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.processing import clean_and_validate_products
from app.recommendation import (
    calculate_scores,
    generate_recommendations,
)


def main():
    # Load the sample dataset.
    data_file = PROJECT_ROOT / "data" / "sample_products.csv"
    products = pd.read_csv(data_file)

    # Clean and validate the data first.
    cleaned, rejected = clean_and_validate_products(products)

    if not rejected.empty:
        print("Some records failed validation:")
        print(rejected.to_string(index=False))
        return

    # Calculate Buy Scores.
    scored = calculate_scores(cleaned)

    print("\n--- PRODUCT BUY SCORES ---")
    print(
        scored[
            [
                "store",
                "product_name",
                "price",
                "rating",
                "review_count",
                "availability",
                "buy_score",
            ]
        ].to_string(index=False)
    )

    # Generate recommendations.
    recommendations = generate_recommendations(scored)

    print("\n--- RECOMMENDATIONS ---")

    labels = {
        "best_overall": "Best Overall",
        "cheapest": "Cheapest",
        "best_rated": "Best Rated",
        "best_value": "Best Value",
    }

    for model, results in recommendations.items():
        print(f"\nProduct model: {model}")

        for category, product in results.items():
            print(
                f"{labels[category]}: {product['store']} | "
                f"{product['product_name']} | "
                f"₹{product['price']} | "
                f"Buy Score: {product['buy_score']}"
            )

    # Test whether changing the weights affects the scores.
    price_focused_weights = {
        "price": 0.60,
        "rating": 0.20,
        "reviews": 0.10,
        "availability": 0.10,
    }

    price_focused = calculate_scores(
        cleaned, weights=price_focused_weights
    )

    print("\n--- PRICE-FOCUSED SCORES ---")
    print(
        price_focused[
            ["store", "product_name", "buy_score"]
        ].to_string(index=False)
    )

    # Basic checks.
    assert len(scored) == len(cleaned)
    assert scored["buy_score"].between(0, 100).all()
    assert len(recommendations) == cleaned["model"].nunique()

    print("\nAll recommendation tests passed!")


if __name__ == "__main__":
    main()
