
import pandas as pd


def match_products(df):
    """
    Group listings that share the same brand and model.

    Returns a copy of the dataset with a product_group
    column identifying each matched product.
    """

    df = df.copy()

    required_columns = ["brand", "model"]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(
                f"Missing required column: {column}"
            )

    # Normalize text for matching without changing
    # the original displayed product names.
    brand_key = (
        df["brand"]
        .astype("string")
        .str.strip()
        .str.casefold()
    )

    model_key = (
        df["model"]
        .astype("string")
        .str.strip()
        .str.casefold()
    )

    # Missing brand/model values must not be grouped
    # together as if they identify the same product.
    valid_key = (
        brand_key.notna()
        & brand_key.ne("")
        & model_key.notna()
        & model_key.ne("")
    )

    df["product_group"] = pd.Series(
        pd.NA, index=df.index, dtype="string"
    )

    keys = brand_key[valid_key] + "|" + model_key[valid_key]

    group_numbers = pd.factorize(keys)[0] + 1

    df.loc[valid_key, "product_group"] = [
        f"PRODUCT_{number:03d}"
        for number in group_numbers
    ]

    return df
