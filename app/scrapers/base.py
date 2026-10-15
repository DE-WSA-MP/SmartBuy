
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


def standardize_store_data(records, store_name):
    """
    Convert scraped product records into SmartBuy's standard format.

    Each scraper should extract website-specific data and pass
    a list of dictionaries to this function.
    """

    if not records:
        return pd.DataFrame(columns=REQUIRED_COLUMNS)

    df = pd.DataFrame(records)

    # Identify missing fields instead of silently inventing values.
    missing = set(REQUIRED_COLUMNS) - set(df.columns)

    if missing:
        raise ValueError(
            f"{store_name} scraper is missing fields: "
            f"{', '.join(sorted(missing))}"
        )

    df = df[REQUIRED_COLUMNS].copy()

    # Use the configured store name consistently.
    df["store"] = store_name

    return df
