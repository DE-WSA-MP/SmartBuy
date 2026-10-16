from pathlib import Path
import csv
from flask import Flask, abort, jsonify, render_template

BASE = Path(__file__).resolve().parent
app = Flask(__name__)
CATEGORIES = ["Smartphones", "Laptops", "Audio"]

def load_products():
    with (BASE / "data" / "products.csv").open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

PRODUCTS = load_products()

@app.get("/")
def index():
    # Product cards are deliberately rendered by static/js/store.js.
    return render_template("index.html", categories=CATEGORIES)

@app.get("/api/products")
def api_products():
    return jsonify({"store": "S08", "products": PRODUCTS, "categories": CATEGORIES})

@app.get("/health")
def health():
    return {"status": "ok", "store": "S08", "listing_count": len(PRODUCTS), "rendering": "javascript"}

@app.get("/category/<path:category>")
def category(category):
    found = next((c for c in CATEGORIES if c.casefold() == category.casefold()), None)
    if found is None:
        abort(404)
    return render_template("index.html", categories=CATEGORIES, initial_category=found)

@app.get("/product/<slug>")
def product(slug):
    item = next((p for p in PRODUCTS if p["product_slug"] == slug), None)
    if item is None:
        abort(404)
    return render_template("product.html", p=item, categories=CATEGORIES)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5008, debug=False)
