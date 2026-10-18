"""Run SmartBuy and all ten dummy storefronts on one local server.
Branch Testing by Janvi 
Start from the repository root with: python run.py
Main SmartBuy stays at /; storefronts are mounted at /store01/ ... /store10/.
"""
from __future__ import annotations

import importlib.util
import math
import re
import sys
from pathlib import Path
from typing import Any

from flask import abort, redirect, render_template, request
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app  # noqa: E402  (project app must load after ROOT is on sys.path)

main_app = create_app()

STORE_DETAILS = {
    "store_01": {"prefix": "/store01", "name": "Northstar Market"},
    "store_02": {"prefix": "/store02", "name": "Fern & Form"},
    "store_03": {"prefix": "/store03", "name": "Signal Supply"},
    "store_04": {"prefix": "/store04", "name": "HomeGrid"},
    "store_05": {"prefix": "/store05", "name": "Orbit Goods"},
    "store_06": {"prefix": "/store06", "name": "Store 06"},
    "store_07": {"prefix": "/store07", "name": "FIELDWORK"},
    "store_08": {"prefix": "/store08", "name": "MONOCHROME"},
    "store_09": {"prefix": "/store09", "name": "GOODFORM"},
    "store_10": {"prefix": "/store10", "name": "ODD / EVEN"},
}
DEFAULT_WEIGHTS = {"price": 0.40, "rating": 0.25, "reviews": 0.20, "availability": 0.15}


def _load_mounted_stores() -> tuple[dict[str, Any], dict[str, Any]]:
    """Load each independent Flask app and prepare its assets/templates for its mount."""
    mounts: dict[str, Any] = {}
    modules: dict[str, Any] = {}
    missing: list[str] = []

    for folder, details in STORE_DETAILS.items():
        app_path = ROOT / "dummy_stores" / folder / "app.py"
        if not app_path.is_file():
            missing.append(str(app_path.relative_to(ROOT)))
            continue

        module_name = f"smartbuy_mounted_{folder}"
        spec = importlib.util.spec_from_file_location(module_name, app_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Could not load storefront module: {app_path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        store_app = getattr(module, "app", None)
        if store_app is None:
            raise RuntimeError(f"{app_path} must expose a Flask instance named 'app'.")

        store_root = app_path.parent.resolve()
        store_app.root_path = str(store_root)
        store_app.template_folder = str(store_root / "templates")
        static_dir = store_root / "static"
        if static_dir.is_dir():
            store_app.static_folder = str(static_dir)

        mounts[details["prefix"]] = store_app
        modules[folder] = module

    if missing:
        missing_text = "\n  - ".join(missing)
        raise RuntimeError(
            "SmartBuy expects all 10 storefront applications before starting. "
            "The following files were not found:\n  - " + missing_text
        )
    return mounts, modules


mounted_apps, store_modules = _load_mounted_stores()


def _float(value: Any, default: float | None = None) -> float | None:
    if value is None:
        return default
    if isinstance(value, (float, int)):
        return float(value)
    cleaned = re.sub(r"[^0-9.\-]", "", str(value).replace(",", ""))
    try:
        return float(cleaned) if cleaned else default
    except ValueError:
        return default


def _count(value: Any, fallback_text: Any = "") -> int:
    """Normalize numeric review fields and human-readable forms such as 5.6K."""
    if isinstance(value, (int, float)):
        return max(0, int(value))
    text = str(value or fallback_text or "").strip().casefold().replace(",", "")
    match = re.search(r"(\d+(?:\.\d+)?)\s*([km])?", text)
    if not match:
        # Try the alternate display field if the primary field was non-numeric text.
        text = str(fallback_text or "").strip().casefold().replace(",", "")
        match = re.search(r"(\d+(?:\.\d+)?)\s*([km])?", text)
    if not match:
        return 0
    amount = float(match.group(1))
    suffix = match.group(2)
    if suffix == "k":
        amount *= 1_000
    elif suffix == "m":
        amount *= 1_000_000
    return max(0, int(amount))


def _rating(product: dict[str, Any]) -> float:
    raw = _float(product.get("rating_raw_value", product.get("rating_value", product.get("rating"))))
    if raw is None:
        # A few store packages only publish formatted rating text.
        raw = _float(product.get("rating_text"))
    if raw is None:
        return 0.0
    scale = _float(product.get("rating_scale_max"), 5.0) or 5.0
    # Preserve the documented rating scale: e.g. 86/100 becomes 4.3/5.
    if scale > 5:
        raw = raw / scale * 5
    return round(min(5.0, max(0.0, raw)), 2)


def _availability_score(value: Any) -> float:
    status = str(value or "").strip().casefold()
    if any(term in status for term in ("out of stock", "sold out", "unavailable", "discontinued", "not available")):
        return 0.0
    if "pre-order" in status or "preorder" in status or "backorder" in status or "back-order" in status:
        return 55.0
    if any(term in status for term in ("in stock", "available", "limited", "only ", "ready to ship", "dispatch")):
        return 100.0
    return 50.0  # Unknown is not automatically treated as out of stock.


def _normalize_store_products() -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for folder, module in store_modules.items():
        details = STORE_DETAILS[folder]
        raw_products = getattr(module, "PRODUCTS", []) or []
        for raw in raw_products:
            title = str(raw.get("title") or raw.get("product_name") or raw.get("name") or "").strip()
            if not title:
                continue
            price = _float(raw.get("price_value_inr", raw.get("price_value", raw.get("price"))))
            if price is None or price <= 0:
                continue
            brand = str(raw.get("brand") or "Unknown brand").strip()
            model = str(raw.get("model_text") or raw.get("model") or title).strip()
            category = str(raw.get("category") or "Uncategorised").strip()
            availability = str(raw.get("availability_raw") or raw.get("availability") or "Unknown").strip()
            reviews = _count(raw.get("review_count_value"), raw.get("review_count_text", ""))
            rating = _rating(raw)
            slug = str(raw.get("product_slug") or "").strip()
            slug = re.sub(r"[^A-Za-z0-9_-]", "", slug)
            product_path = f"{details['prefix']}/product/{slug}" if slug else f"{details['prefix']}/"
            normalized.append({
                "product_id": str(raw.get("listing_id") or f"{folder}-{len(normalized)+1}"),
                "store": details["name"],
                "store_id": folder[-2:],
                "product_name": title,
                "brand": brand,
                "model": model,
                "category": category,
                "price": round(price, 2),
                "rating": rating,
                "review_count": reviews,
                "availability": availability,
                "product_url": product_path,
                "_availability_score": _availability_score(availability),
            })
    return normalized


STORE_PRODUCTS = _normalize_store_products()


def _search_matches(query: str) -> list[dict[str, Any]]:
    terms = [part for part in re.findall(r"[\w]+", query.casefold()) if part]
    if not terms:
        return []
    matches = []
    for product in STORE_PRODUCTS:
        haystack = " ".join((
            product["product_name"], product["brand"], product["model"], product["category"], product["store"]
        )).casefold()
        if all(term in haystack for term in terms):
            matches.append(product.copy())
    return matches


def _request_weights() -> dict[str, float]:
    if request.form.get("apply_weights") != "1":
        return DEFAULT_WEIGHTS.copy()
    raw = {}
    for key, default in DEFAULT_WEIGHTS.items():
        value = _float(request.form.get(f"{key}_weight"), default * 100)
        raw[key] = max(0.0, min(100.0, value if value is not None else default * 100))
    total = sum(raw.values())
    if total <= 0:
        return DEFAULT_WEIGHTS.copy()
    return {key: value / total for key, value in raw.items()}


def _score_products(products: list[dict[str, Any]], weights: dict[str, float]) -> list[dict[str, Any]]:
    if not products:
        return products
    prices = [p["price"] for p in products]
    min_price, max_price = min(prices), max(prices)
    max_reviews = max((p["review_count"] for p in products), default=0)
    max_log_reviews = math.log1p(max_reviews) if max_reviews > 0 else 1.0

    for product in products:
        price_score = 100.0 if max_price == min_price else (max_price - product["price"]) / (max_price - min_price) * 100.0
        rating_score = product["rating"] / 5.0 * 100.0
        review_score = math.log1p(product["review_count"]) / max_log_reviews * 100.0 if product["review_count"] else 0.0
        availability_score = product["_availability_score"]
        contributions = {
            "price": price_score * weights["price"],
            "rating": rating_score * weights["rating"],
            "reviews": review_score * weights["reviews"],
            "availability": availability_score * weights["availability"],
        }
        product["buy_score"] = round(sum(contributions.values()), 2)
        product["_contributions"] = contributions
        product["_metric_scores"] = {
            "price": price_score, "rating": rating_score,
            "reviews": review_score, "availability": availability_score,
        }
        candidates = [
            (contributions["price"], f"Price: ₹{product['price']:,.0f}"),
            (contributions["rating"], f"Rating: {product['rating']:.1f}/5"),
            (contributions["reviews"], f"Reviews: {product['review_count']:,}"),
            (contributions["availability"], f"Availability: {product['availability']}"),
        ]
        product["_reasons"] = [reason for _, reason in sorted(candidates, reverse=True)[:3]]
    return products


def _make_recommendations(products: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for product in products:
        group_key = f"{product['brand']} {product['model']}".casefold()
        groups.setdefault(group_key, []).append(product)

    recommendations: dict[str, dict[str, Any]] = {}
    for listings in groups.values():
        best_overall = max(listings, key=lambda p: p["buy_score"])
        cheapest = min(listings, key=lambda p: p["price"])
        best_rated = max(listings, key=lambda p: (p["rating"], p["review_count"]))
        # Best value emphasises the balanced score but avoids duplicating a tie by preferring lower price.
        best_value = max(listings, key=lambda p: (p["buy_score"], -p["price"]))

        def choice(item: dict[str, Any], explain: bool = False) -> dict[str, Any]:
            result = {key: item[key] for key in ("store", "product_name", "price", "rating", "review_count", "buy_score", "product_url")}
            if explain:
                result["explanation"] = {
                    "reasons": item["_reasons"],
                    "contributions": item["_contributions"],
                }
            return result

        group_name = f"{best_overall['brand']} {best_overall['model']}"
        recommendations[group_name] = {
            "best_overall": choice(best_overall, explain=True),
            "cheapest": choice(cheapest),
            "best_rated": choice(best_rated),
            "best_value": choice(best_value),
        }
    return recommendations


def _sample_search_fallback():
    """Preserve SmartBuy's existing sample-data route when the user selects it."""
    for endpoint in ("main.search", "search"):
        view = main_app.view_functions.get(endpoint)
        if view is not None:
            return view()
    abort(500, description="The existing Sample Data search view could not be found in the main app.")


def network_search():
    source = str(request.values.get("source", "stores")).strip().casefold()
    if source in {"sample", "sample_data"}:
        return _sample_search_fallback()

    query = str(request.values.get("product", "")).strip()
    if not query:
        # GET without a query simply returns the user to the main landing page.
        return redirect("/")

    weights = _request_weights()
    products = _score_products(_search_matches(query), weights)
    products.sort(key=lambda item: item["buy_score"], reverse=True)
    message = None
    recommendations: dict[str, dict[str, Any]] = {}
    if not products:
        message = (
            f"No matching listings were found for '{query}' in the ten-store catalogue. "
            "Try a brand, model, or a shorter product name."
        )
    else:
        recommendations = _make_recommendations(products)

    return render_template(
        "results.html",
        query=query,
        source="stores",
        products=products,
        recommendations=recommendations,
        weights=weights,
        message=message,
    )


if "smartbuy_network_search" not in main_app.view_functions:
    main_app.add_url_rule(
        "/network-search",
        endpoint="smartbuy_network_search",
        view_func=network_search,
        methods=["GET", "POST"],
    )

# Keep the main SmartBuy experience at / and mount each independent storefront below it.
application = DispatcherMiddleware(main_app, mounted_apps)
# Keep the conventional WSGI variable name available; it must be the composite app.
app = application

if __name__ == "__main__":
    print("\nSmartBuy is starting on one local server.")
    print("Main website:   http://127.0.0.1:8000/")
    print("Storefronts:    http://127.0.0.1:8000/store01/ through /store10/")
    print("Stop the server with Ctrl+C.\n")
    run_simple(
        "127.0.0.1",
        8000,
        application,
        use_reloader=True,
        use_debugger=True,
        threaded=True,
    )
