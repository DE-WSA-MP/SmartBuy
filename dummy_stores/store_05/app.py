from pathlib import Path
from flask import Flask, abort, jsonify, render_template, request, url_for
import csv

BASE = Path(__file__).resolve().parent
app = Flask(__name__)

def load_products():
    with (BASE / "data" / "products.csv").open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

PRODUCTS = load_products()

@app.get("/")
def index():
    categories = sorted({p["category"] for p in PRODUCTS})
    return render_template("index.html", categories=categories)

@app.get("/health")
def health():
    return {"status": "ok", "store": "S05", "listing_count": len(PRODUCTS)}

@app.get("/api/products")
def api_products():
    # Public response intentionally contains store-facing fields only, never canonical IDs.
    q = request.args.get("q", "").strip().casefold()
    found = [p for p in PRODUCTS if not q or q in p["title"].casefold() or q in p["brand"].casefold() or q in p["category"].casefold()]
    return jsonify([{
        "listing_id": p["listing_id"], "title": p["title"], "category": p["category"],
        "brand": p["brand"], "price_text": p["price_text"], "rating_text": p["rating_text"],
        "review_count_text": p["review_count_text"], "availability": p["availability_raw"],
        "product_url": url_for("product", slug=p["product_slug"])
    } for p in found])

@app.get("/product/<slug>")
def product(slug):
    item = next((p for p in PRODUCTS if p["product_slug"] == slug), None)
    if item is None:
        abort(404)
    return render_template("product.html", p=item)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5005, debug=False)
