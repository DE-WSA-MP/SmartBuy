from pathlib import Path
import csv
from flask import Flask, abort, render_template, request

BASE = Path(__file__).resolve().parent
app = Flask(__name__)

def load_products():
    with (BASE / "data" / "products.csv").open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

PRODUCTS = load_products()

@app.get("/")
def index():
    categories = sorted({p["category"] for p in PRODUCTS})
    return render_template("index.html", products=PRODUCTS, categories=categories, query="")

@app.get("/health")
def health():
    return {"status": "ok", "store": "S01", "listing_count": len(PRODUCTS)}

@app.get("/search")
def search():
    q = request.args.get("q", "").strip().casefold()
    found = [p for p in PRODUCTS if q in p["title"].casefold() or q in p["brand"].casefold() or q in p["category"].casefold()]
    return render_template("index.html", products=found, categories=sorted({p["category"] for p in PRODUCTS}), query=q)

@app.get("/category/<path:category>")
def category(category):
    found = [p for p in PRODUCTS if p["category"].casefold() == category.casefold()]
    return render_template("index.html", products=found, categories=sorted({p["category"] for p in PRODUCTS}), query="")

@app.get("/product/<slug>")
def product(slug):
    item = next((p for p in PRODUCTS if p["product_slug"] == slug), None)
    if item is None:
        abort(404)
    return render_template("product.html", p=item)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)
