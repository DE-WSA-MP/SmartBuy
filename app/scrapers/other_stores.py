
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


HUB = "http://127.0.0.1:8000"
HEADERS = {"User-Agent": "SmartBuy-Development/1.0"}
TIMEOUT = 15


def _text(element):
    return element.get_text(" ", strip=True) if element else ""


def _number(value):
    if value is None:
        return None
    match = re.search(r"[\d,]+(?:\.\d+)?", str(value))
    return float(match.group().replace(",", "")) if match else None


def _count(value):
    """Parse counts such as 2,300, 845, or 5.6K."""
    if not value:
        return 0

    match = re.search(r"([\d,.]+)\s*([KkMm])?", str(value))
    if not match:
        return 0

    number = float(match.group(1).replace(",", ""))
    suffix = (match.group(2) or "").lower()

    if suffix == "k":
        number *= 1000
    elif suffix == "m":
        number *= 1_000_000

    return int(number)


def _rating(value, scale=5):
    number = _number(value)
    if number is None:
        return None

    if scale == 100:
        number /= 20

    return min(5.0, max(0.0, number))



def _availability(value):
    value = (value or "").strip().casefold()

    if any(term in value for term in (
        "out of stock",
        "unavailable",
        "sold out",
    )):
        return "Out of Stock"

    if "pre-order" in value or "preorder" in value:
        return "Pre-order"

    if any(term in value for term in (
        "in stock",
        "available",
        "left",
        "limited",
    )):
        return "In Stock"

    return "Unknown"


def _record(product_id, store, name, brand, price, rating,
            reviews, availability, product_url):
    brand = (brand or "").strip()

    if not name or price is None:
        return None

    if not brand:
        brand = name.split()[0]

    model = name[len(brand):].strip() if name.casefold().startswith(
        brand.casefold()
    ) else name

    return {
        "product_id": str(product_id),
        "store": store,
        "product_name": name.strip(),
        "brand": brand,
        "model": model,
        "price": price,
        "rating": rating,
        "review_count": reviews,
        "availability": availability,
        "product_url": product_url,
    }


def _fetch_html(store_number):
    base = f"{HUB}/store{store_number:02d}/"
    response = requests.get(base, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    return base, BeautifulSoup(response.text, "html.parser")


def _scrape_html(store_number, store_name):
    base, soup = _fetch_html(store_number)
    products = []

    # Store 10 uses product rows rather than product cards.
    if store_number == 10:
        cards = soup.select("article.product-row")
    elif store_number == 2:
        cards = soup.select("article.product-card")
    elif store_number == 3:
        cards = soup.select("article.product-card")
    else:
        cards = soup.select("article.card")

    for card in cards:
        link = card.select_one("h3 a")
        if not link:
            continue

        name = _text(link)
        href = link.get("href", "")
        product_url = urljoin(base, href)
        product_id = product_url.rstrip("/").split("/")[-1]

        if store_number == 2:
            price_text = _text(card.select_one(".price-line strong"))
            rating_text = _text(card.select_one(".rating"))
            review_text = rating_text
            brand = ""
            stock_text = _text(card.select_one(".stock"))

        elif store_number == 3:
            price_text = _text(card.select_one(".product-bottom strong"))
            rating_text = _text(card.select_one(".rating"))
            review_text = rating_text
            brand = _text(card.select_one(".brand")).split("·")[0]
            stock_text = _text(card.select_one(".stock"))

        elif store_number == 4:
            price_text = _text(card.select_one(".price-row strong"))
            rating_text = _text(card.select_one(".sr-rating"))
            review_text = _text(card.select_one(".rating small"))
            brand = _text(card.select_one(".brand")).split("·")[0]
            stock_text = _text(card.select_one(".stock"))

        elif store_number == 6:
            price_text = _text(card.select_one(".price-line strong"))
            rating_text = _text(card.select_one(".rating b"))
            review_text = _text(card.select_one(".reviews"))
            brand = _text(card.select_one(".brand")).split("/")[0]
            stock_text = _text(card.select_one(".stock"))

        elif store_number in (7, 9):
            price_text = _text(card.select_one(".price strong"))
            rating_text = _text(card.select_one(".rating b"))
            review_text = _text(card.select_one(".reviews"))
            brand = _text(card.select_one(".brand")).split(
                "—" if store_number == 7 else "/"
            )[0]
            stock_text = _text(card.select_one(".stock"))

        else:  # Store 10
            price_text = _text(card.select_one(".row-price strong"))
            rating_text = _text(card.select_one(".row-rating"))
            review_text = rating_text
            category_brand = _text(card.select_one(".row-category"))
            brand = category_brand.split("/")[-1].strip()
            stock_text = _text(card.select_one(".row-status"))

        price = _number(price_text)
        rating = _rating(rating_text)
        review_count = _count(review_text)

        # Explicitly preserve missing ratings instead of inventing one.
        if price is None:
            continue

        record = _record(
            product_id=product_id,
            store=store_name,
            name=name,
            brand=brand,
            price=price,
            rating=rating,
            reviews=review_count,
            availability=_availability(stock_text),
            product_url=product_url,
        )

        if record:
            products.append(record)

    return products


def _scrape_store_05():
    store_name = "Orbit Goods"
    url = f"{HUB}/store05/api/products"

    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    data = response.json()

    if not isinstance(data, list):
        raise ValueError("Store 05 API did not return a product list.")

    products = []

    for item in data:
        name = item.get("title", "")
        product_url = urljoin(HUB + "/", item.get("product_url", ""))
        price = _number(item.get("price_text"))
        rating = _rating(item.get("rating_text"), scale=100)

        record = _record(
            product_id=item.get("listing_id") or product_url,
            store=store_name,
            name=name,
            brand=item.get("brand", ""),
            price=price,
            rating=rating,
            reviews=_count(item.get("review_count_text")),
            availability=_availability(item.get("availability")),
            product_url=product_url,
        )

        if record:
            products.append(record)

    return products


def _scrape_store_08():
    store_name = "Monochrome"
    url = f"{HUB}/store08/api/products"

    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    data = response.json()

    items = data.get("products", []) if isinstance(data, dict) else data
    if not isinstance(items, list):
        raise ValueError("Store 08 API did not return a product list.")

    products = []

    for item in items:
        name = item.get("title", "")
        slug = item.get("product_slug", "")
        product_url = urljoin(
            f"{HUB}/store08/",
            f"product/{slug}" if slug else "",
        )

        price = _number(item.get("price_value_inr"))
        if price is None:
            price = _number(item.get("price_text"))

        rating = _rating(
            item.get("rating_raw_value", item.get("rating_text"))
        )

        record = _record(
            product_id=item.get("listing_id") or slug or product_url,
            store=store_name,
            name=name,
            brand=item.get("brand", ""),
            price=price,
            rating=rating,
            reviews=_count(
                item.get("review_count_value", item.get("review_count_text"))
            ),
            availability=_availability(item.get("availability_raw")),
            product_url=product_url,
        )

        if record:
            products.append(record)

    return products


def scrape_store_02():
    return _scrape_html(2, "Fern & Form")


def scrape_store_03():
    return _scrape_html(3, "Signal Supply")


def scrape_store_04():
    return _scrape_html(4, "HomeGrid")


def scrape_store_05():
    return _scrape_store_05()


def scrape_store_06():
    return _scrape_html(6, "Pulse & Co.")


def scrape_store_07():
    return _scrape_html(7, "Fieldwork")


def scrape_store_08():
    return _scrape_store_08()


def scrape_store_09():
    return _scrape_html(9, "Goodform")


def scrape_store_10():
    return _scrape_html(10, "Odd / Even")
