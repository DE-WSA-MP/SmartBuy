
from app.scrapers.runner import run_scrapers

SCRAPERS = {}


def register_scraper(store_name, scraper_function):
    if not isinstance(store_name, str) or not store_name.strip():
        raise ValueError("Store name must be a non-empty string.")

    if not callable(scraper_function):
        raise TypeError("Scraper function must be callable.")

    SCRAPERS[store_name.strip()] = scraper_function


def get_registered_scrapers():
    return SCRAPERS.copy()


def collect_from_registered_stores():
    return run_scrapers(get_registered_scrapers())
