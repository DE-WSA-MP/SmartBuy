
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


STORE_NAME = "Northstar Market"
STORE_URL = "http://127.0.0.1:8000/store01/"


def _text(element):
    return element.get_text(" ", strip=True) if element else ""


def _number(text):
    match = re.search(r"[\d,]+(?:\.\d+)?", text or "")
    return float(match.group().replace(",", "")) if match else None


def scrape_store_01():
    response = requests.get(
        STORE_URL,
        timeout=15,
        headers={"User-Agent": "SmartBuy-Development/1.0"},
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.select("article.product-card")
    products = []

    for card in cards:
        link = card.select_one(".product-info h3 a")
        price_element = card.select_one(".price")
        rating_element = card.select_one(".rating")
        stock_element = card.select_one(".stock")

        if not link or not price_element:
            continue

        product_name = _text(link)
        price = _number(_text(price_element))

        if not product_name or price is None:
            continue

        rating_text = _text(rating_element)
        rating = _number(rating_text)
        review_match = re.search(
            r"\(([\d,]+)\s+reviews?\)",
            rating_text,
            re.IGNORECASE,
        )
        review_count = (
            int(review_match.group(1).replace(",", ""))
            if review_match
            else 0
        )

        stock_text = _text(stock_element).casefold()
        availability = (
            "Out of Stock"
            if "out of stock" in stock_text
            else "In Stock"
        )

        # The catalogue has no separate brand/model fields.
        # Keep these conservative; the matching pipeline can normalize
        # them later.
        brand = product_name.split()[0]
        model = product_name[len(brand):].strip()

        product_url = urljoin(STORE_URL, link.get("href", ""))

        products.append(
            {
                "product_id": product_url.rstrip("/").split("/")[-1],
                "store": STORE_NAME,
                "product_name": product_name,
                "brand": brand,
                "model": model,
                "price": price,
                "rating": rating,
                "review_count": review_count,
                "availability": availability,
                "product_url": product_url,
            }
        )

    return products
