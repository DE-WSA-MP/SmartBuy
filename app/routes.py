
from flask import Blueprint, render_template, request

from app.pipeline import get_comparison_results
from app.recommendation import DEFAULT_WEIGHTS

main = Blueprint("main", __name__)


def render_search_results(query, weights=None, source="sample", error=None):
    if weights is None:
        weights = DEFAULT_WEIGHTS.copy()

    if error:
        return render_template(
            "results.html",
            query=query,
            products=[],
            recommendations={},
            weights=weights,
            source=source,
            scraper_status={},
            message=error,
        )

    if not query:
        return render_template(
            "results.html",
            query="",
            products=[],
            recommendations={},
            weights=weights,
            source=source,
            scraper_status={},
            message="Please enter a product to search.",
        )

    try:
        result = get_comparison_results(
            query,
            weights=weights,
            source=source,
        )
    except (ValueError, TypeError) as exc:
        return render_search_results(
            query,
            weights=weights,
            source=source,
            error=str(exc),
        )

    products = result["products"]

    if products:
        message = None
    elif source == "scrape":
        message = (
            "No matching products were found in the registered stores. "
            "Check the store scraper status below."
        )
    else:
        message = "No matching products were found in the sample data."

    return render_template(
        "results.html",
        query=result["query"],
        products=products,
        recommendations=result["recommendations"],
        weights=weights,
        source=source,
        scraper_status=result.get("scraper_status", {}),
        rejected_count=result.get("rejected_count", 0),
        message=message,
    )


@main.route("/")
def home():
    return render_template("index.html")


@main.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        query = request.form.get("product", "").strip()
        source = request.form.get("source", "sample")

        if request.form.get("apply_weights") == "1":
            try:
                weights = {
                    "price": float(request.form.get("price_weight", 40)),
                    "rating": float(request.form.get("rating_weight", 30)),
                    "reviews": float(request.form.get("reviews_weight", 20)),
                    "availability": float(
                        request.form.get("availability_weight", 10)
                    ),
                }
            except (TypeError, ValueError):
                return render_search_results(
                    query,
                    source=source,
                    error="Please enter valid numbers for all weights.",
                )

            if any(value < 0 or value > 100 for value in weights.values()):
                return render_search_results(
                    query,
                    weights=weights,
                    source=source,
                    error="Each weight must be between 0 and 100.",
                )

            if sum(weights.values()) <= 0:
                return render_search_results(
                    query,
                    weights=weights,
                    source=source,
                    error="The total weight must be greater than zero.",
                )
        else:
            weights = DEFAULT_WEIGHTS.copy()

    else:
        query = request.args.get("product", "").strip()
        source = request.args.get("source", "sample")
        weights = DEFAULT_WEIGHTS.copy()

    if source not in {"sample", "scrape"}:
        source = "sample"

    return render_search_results(
        query,
        weights=weights,
        source=source,
    )
