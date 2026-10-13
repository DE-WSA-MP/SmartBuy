
from flask import Blueprint, render_template, request

from app.pipeline import get_comparison_results

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template("index.html")


@main.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        query = request.form.get("product", "").strip()
    else:
        query = request.args.get("product", "").strip()

    if not query:
        return render_template(
            "results.html",
            query="",
            products=[],
            recommendations={},
            message="Please enter a product name to search.",
        )

    result = get_comparison_results(query)

    if result is None:
        return render_template(
            "results.html",
            query=query,
            products=[],
            recommendations={},
            message="Please enter a product name to search.",
        )

    message = None

    if not result["products"]:
        message = f"No products found for '{query}'. Try another search."

    return render_template(
        "results.html",
        query=query,
        products=result["products"],
        recommendations=result["recommendations"],
        message=message,
    )
