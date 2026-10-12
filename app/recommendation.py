
import pandas as pd


DEFAULT_WEIGHTS = {
    "price": 0.40,
    "rating": 0.30,
    "reviews": 0.20,
    "availability": 0.10,
}


def calculate_scores(products, weights=None):
    """
    Calculate a Buy Score between 0 and 100 for each listing.

    Products should already be cleaned and matched to a common
    product model or group.
    """

    df = products.copy()

    weights = DEFAULT_WEIGHTS.copy() if weights is None else weights.copy()

    # Validate the supplied weights.
    if set(weights) != set(DEFAULT_WEIGHTS):
        raise ValueError(
            "Weights must contain price, rating, reviews, availability."
        )

    if any(not isinstance(v, (int, float)) or v < 0 for v in weights.values()):
        raise ValueError("Weights must be non-negative numbers.")

    total_weight = sum(weights.values())

    if total_weight <= 0:
        raise ValueError("At least one weight must be greater than zero.")

    # Normalize weights so they always total 100%.
    weights = {
        key: value / total_weight
        for key, value in weights.items()
    }

    # Convert inputs to numeric values.
    for column in ["price", "rating", "review_count"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Availability score: 1 if in stock, otherwise 0.
    df["availability_score"] = (
        df["availability"].astype(str).str.strip().str.casefold()
        .isin(["in stock", "available"])
        .astype(float)
    )

    # Calculate scores separately for each model.
    # This avoids comparing the price of a phone with another
    # completely different product.
    group_column = (
        "product_group" if "product_group" in df.columns else "model"
    )

    if group_column not in df.columns:
        raise ValueError("A product_group or model column is required.")

    df["price_score"] = 0.0
    df["rating_score"] = (df["rating"] / 5).clip(0, 1)
    df["review_score"] = 0.0

    for _, indexes in df.groupby(group_column, dropna=False).groups.items():
        group = df.loc[indexes]

        min_price = group["price"].min()
        max_price = group["price"].max()

        if pd.isna(min_price) or pd.isna(max_price):
            df.loc[indexes, "price_score"] = 0.0
        elif max_price == min_price:
            # Equal prices mean no listing has a price advantage.
            df.loc[indexes, "price_score"] = 1.0
        else:
            df.loc[indexes, "price_score"] = (
                (max_price - group["price"]) / (max_price - min_price)
            )

        min_reviews = group["review_count"].min()
        max_reviews = group["review_count"].max()

        if pd.isna(min_reviews) or pd.isna(max_reviews):
            df.loc[indexes, "review_score"] = 0.0
        elif max_reviews == min_reviews:
            df.loc[indexes, "review_score"] = 1.0
        else:
            df.loc[indexes, "review_score"] = (
                (group["review_count"] - min_reviews)
                / (max_reviews - min_reviews)
            )

    # Weighted sum, expressed as a percentage.
    df["buy_score"] = 100 * (
        weights["price"] * df["price_score"]
        + weights["rating"] * df["rating_score"]
        + weights["reviews"] * df["review_score"]
        + weights["availability"] * df["availability_score"]
    )

    df["buy_score"] = df["buy_score"].round(2)

    return df


def generate_recommendations(scored_products):
    """
    Generate recommendations for each matched product group.
    """

    group_column = (
        "product_group"
        if "product_group" in scored_products.columns
        else "model"
    )

    recommendations = {}

    for group_name, group in scored_products.groupby(
        group_column, dropna=False
    ):
        available = group[group["availability_score"] == 1]

        # Prefer in-stock listings for purchase recommendations.
        candidates = available if not available.empty else group

        best_overall = candidates.sort_values(
            ["buy_score", "price"],
            ascending=[False, True],
        ).iloc[0]

        cheapest = candidates.sort_values(
            ["price", "buy_score"],
            ascending=[True, False],
        ).iloc[0]

        best_rated = candidates.sort_values(
            ["rating", "review_count"],
            ascending=[False, False],
        ).iloc[0]

        best_value = candidates.sort_values(
            ["buy_score", "price"],
            ascending=[False, True],
        ).iloc[0]

        recommendations[group_name] = {
            "best_overall": best_overall.to_dict(),
            "cheapest": cheapest.to_dict(),
            "best_rated": best_rated.to_dict(),
            "best_value": best_value.to_dict(),
        }

    return recommendations
