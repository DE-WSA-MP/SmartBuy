from pathlib import Path
import csv
from flask import Flask, abort, render_template, request

BASE = Path(__file__).resolve().parent
app = Flask(__name__)
CATEGORIES = ["Smartphones", "Audio", "Wearables"]

def load_products():
    with (BASE / "data" / "products.csv").open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

PRODUCTS = load_products()

def filtered_products():
    items = PRODUCTS
    category = request.args.get("category", "").strip()
    query = request.args.get("q", "").strip().casefold()
    if category:
        items = [p for p in items if p["category"].casefold() == category.casefold()]
    if query:
        items = [p for p in items if query in p["title"].casefold() or query in p["brand"].casefold() or query in p["category"].casefold()]
    return items

@app.get("/")
def index():
    return render_template("index.html", products=filtered_products(), categories=CATEGORIES, selected_category=request.args.get("category", ""), query=request.args.get("q", ""))

@app.get("/health")
def health():
    return {"status": "ok", "store": "S06", "listing_count": len(PRODUCTS)}

@app.get("/category/<path:category>")
def category(category):
    found = next((c for c in CATEGORIES if c.casefold() == category.casefold()), None)
    if found is None: abort(404)
    return render_template("index.html", products=[p for p in PRODUCTS if p["category"].casefold() == found.casefold()], categories=CATEGORIES, selected_category=found, query="")

@app.get("/product/<slug>")
def product(slug):
    item = next((p for p in PRODUCTS if p["product_slug"] == slug), None)
    if item is None: abort(404)
    return render_template("product.html", p=item, categories=CATEGORIES)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5006, debug=False)
