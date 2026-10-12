
import pandas as pd


REQUIRED_COLUMNS = [
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


def clean_and_validate_products(df):
    """
    Clean and validate product records collected from stores.

    Returns:
        cleaned_df: valid, standardized product records
        rejected_df: records that failed validation
    """

    df = df.copy()

    # 1. Check whether all required columns are present.
    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # 2. Remove leading/trailing whitespace from text fields.
    text_columns = [
        "product_id",
        "store",
        "product_name",
        "brand",
        "model",
        "availability",
        "product_url",
    ]

    for column in text_columns:
        df[column] = df[column].astype("string").str.strip()

    # Treat empty strings as missing values.
    df[text_columns] = df[text_columns].replace("", pd.NA)

    # 3. Convert numeric fields to numeric types.
    numeric_columns = [
        "price",
        "rating",
        "review_count",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column], errors="coerce"
        )

    # 4. Standardize availability values.
    availability_map = {
        "in stock": "In Stock",
        "out of stock": "Out of Stock",
        "available": "In Stock",
        "unavailable": "Out of Stock",
    }

    df["availability"] = (
        df["availability"]
        .str.casefold()
        .map(availability_map)
    )

    # 5. Identify records with missing required values.
    required_values = [
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

    invalid = df[required_values].isna().any(axis=1)

    # 6. Validate numerical ranges.
    invalid |= df["price"].le(0)
    invalid |= ~df["rating"].between(0, 5)
    invalid |= df["review_count"].lt(0)

    # 7. Reject duplicate listing IDs.
    duplicate_ids = (
        df["product_id"].notna()
        & df["product_id"].duplicated(keep=False)
    )
    invalid |= duplicate_ids

    # 8. Separate valid and rejected records.
    rejected_df = df[invalid].copy()
    cleaned_df = df[~invalid].copy()

    # 9. Remove duplicate records with identical listing data.
    cleaned_df = cleaned_df.drop_duplicates(
        subset=[
            "store",
            "product_name",
            "brand",
            "model",
            "price",
        ]
    )

    return cleaned_df.reset_index(drop=True), rejected_df
