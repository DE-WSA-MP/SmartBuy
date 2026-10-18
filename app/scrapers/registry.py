
from app.scrapers.runner import run_scrapers
from app.scrapers.store_01 import scrape_store_01
from app.scrapers.other_stores import (
    scrape_store_02,
    scrape_store_03,
    scrape_store_04,
    scrape_store_05,
    scrape_store_06,
    scrape_store_07,
    scrape_store_08,
    scrape_store_09,
    scrape_store_10,
)

SCRAPERS = {
    "Northstar Market": scrape_store_01,
    "Fern & Form": scrape_store_02,
    "Signal Supply": scrape_store_03,
    "HomeGrid": scrape_store_04,
    "Orbit Goods": scrape_store_05,
    "Pulse & Co.": scrape_store_06,
    "Fieldwork": scrape_store_07,
    "Monochrome": scrape_store_08,
    "Goodform": scrape_store_09,
    "Odd / Even": scrape_store_10,
}


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
