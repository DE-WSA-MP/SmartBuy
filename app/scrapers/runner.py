
import pandas as pd

from app.scrapers.base import REQUIRED_COLUMNS, standardize_store_data


def run_scrapers(scrapers):
    """
    Run multiple store scrapers independently.

    Parameters
    ----------
    scrapers : dict
        Mapping of store names to scraper functions.
        Each scraper function should return a list of product dictionaries.

    Returns
    -------
    combined_products : pandas.DataFrame
        Combined records from successful scrapers.
    status : dict
        Success or failure details for every store.
    """

    successful_results = []
    status = {}

    for store_name, scraper_function in scrapers.items():
        try:
            records = scraper_function()

            if isinstance(records, pd.DataFrame):
                records = records.to_dict(orient="records")

            if not isinstance(records, list):
                raise TypeError(
                    "Scraper must return a list of product dictionaries."
                )

            store_products = standardize_store_data(
                records,
                store_name,
            )

            successful_results.append(store_products)

            status[store_name] = {
                "success": True,
                "records_found": len(store_products),
                "error": None,
            }

        except Exception as exc:
            # A failed store should not stop the other scrapers.
            status[store_name] = {
                "success": False,
                "records_found": 0,
                "error": str(exc),
            }

    if successful_results:
        combined_products = pd.concat(
            successful_results,
            ignore_index=True,
        )
    else:
        combined_products = pd.DataFrame(columns=REQUIRED_COLUMNS)

    return combined_products, status
