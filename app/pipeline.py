
from app.processing import clean_and_validate_products
from app.matching import match_products
from app.recommendation import (
    calculate_scores,
    generate_recommendations,
    explain_recommendation,
)
from app.database import seed_sample_data, load_products
from app.scrapers.runner import run_scrapers
from app.scrapers.registry import get_registered_scrapers

def get_comparison_results(
    query,
    weights=None,
    source="sample",
    scrapers=None,
):
    """
    Run the SmartBuy pipeline using sample data or live store scrapers.

    source="sample": load products from the existing SQLite database.
    source="scrape": collect products using the supplied scraper functions.
    """

    if not query or not query.strip():
        return None

    scraper_status = {}

    # 1. Acquire data.
    if source == "sample":
        seed_sample_data()
        products = load_products()

    elif source == "scrape":
        active_scrapers = (
            scrapers
            if scrapers is not None
            else get_registered_scrapers()
        )

        if not active_scrapers:
            raise ValueError(
                "No store scrapers are registered yet. "
                "Register at least one scraper before using scraping mode."
            )

        products, scraper_status = run_scrapers(active_scrapers)

    else:
        raise ValueError(
            "Invalid source. Use 'sample' or 'scrape'."
        )

    # 2. Clean and validate the acquired records.
    cleaned, rejected = clean_and_validate_products(products)

    # 3. Match equivalent products across stores.
    matched = match_products(cleaned)

    # 4. Filter listings using the user's search query.
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

    # Preserve acquisition status even when no product matches.
    if matching_products.empty:
        return {
            "query": query.strip(),
            "source": source,
            "products": [],
            "recommendations": {},
            "rejected_count": len(rejected),
            "scraper_status": scraper_status,
        }

    # 5. Calculate Buy Scores using the selected weights.
    scored = calculate_scores(matching_products, weights=weights)

    # 6. Generate recommendations for each matched product group.
    recommendations = generate_recommendations(scored)

    # 7. Explain recommendations using their score components.
    group_column = (
        "product_group"
        if "product_group" in scored.columns
        else "model"
    )

    for group_name, choices in recommendations.items():
        group_products = scored[
            scored[group_column] == group_name
        ]

        for recommendation_type, product in choices.items():
            choices[recommendation_type]["explanation"] = (
                explain_recommendation(
                    product,
                    group_products,
                    weights=weights,
                )
            )

    return {
        "query": query.strip(),
        "source": source,
        "products": scored.to_dict(orient="records"),
        "recommendations": recommendations,
        "rejected_count": len(rejected),
        "scraper_status": scraper_status,
    }
