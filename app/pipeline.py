
from app.processing import clean_and_validate_products
from app.matching import match_products
from app.recommendation import (
    calculate_scores,
    generate_recommendations,
)
from app.database import seed_sample_data, load_products


def get_comparison_results(query, weights=None):
    """
    Load product records, clean them, match equivalent products,
    calculate Buy Scores, and generate recommendations.
    """

    if not query or not query.strip():
        return None

    # 1. Initialize the database and load product records.
    seed_sample_data()
    products = load_products()

    # 2. Clean and validate records.
    cleaned, rejected = clean_and_validate_products(products)

    # 3. Match equivalent products using brand and model.
    matched = match_products(cleaned)

    # 4. Find products relevant to the user's search.
    search_query = query.strip().casefold()

    mask = (
        matched["product_name"].str.casefold().str.contains(
            search_query, regex=False, na=False
        )
        | matched["brand"].str.casefold().str.contains(
            search_query, regex=False, na=False
        )
        | matched["model"].str.casefold().str.contains(
            search_query, regex=False, na=False
        )
    )

    matching_products = matched[mask].copy()

    if matching_products.empty:
        return {
            "query": query.strip(),
            "products": [],
            "recommendations": {},
            "rejected_count": len(rejected),
        }

    # 5. Calculate Buy Scores within each product group.
    scored = calculate_scores(
        matching_products,
        weights=weights,
    )

    # 6. Generate recommendations for each matched group.
    recommendations = generate_recommendations(scored)

    return {
        "query": query.strip(),
        "products": scored.to_dict(orient="records"),
        "recommendations": recommendations,
        "rejected_count": len(rejected),
    }
