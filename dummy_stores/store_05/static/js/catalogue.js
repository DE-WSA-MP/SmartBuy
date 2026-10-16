const mount = document.querySelector("#product-list");
const count = document.querySelector("#result-count");
const search = document.querySelector("#search");
const searchForm = document.querySelector("#search-form");

let activeCategory = "";

function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    }[char]));
}

function render(items) {
    const visible = activeCategory
        ? items.filter(item => item.category === activeCategory)
        : items;

    count.textContent = `${visible.length} items`;

    if (!visible.length) {
        mount.innerHTML =
            '<p class="empty">No products match this search.</p>';
        return;
    }

    mount.innerHTML = visible.map((p, i) => `
        <article class="item-card">
            <div class="item-index">
                ${String(i + 1).padStart(2, "0")}
            </div>
            <div class="item-body">
                <p class="category">${escapeHTML(p.category)}</p>
                <h3>
                    <a href="${escapeHTML(p.product_url)}">
                        ${escapeHTML(p.title)}
                    </a>
                </h3>
                <p class="price">${escapeHTML(p.price_text)}</p>
                <p class="rating">
                    ${escapeHTML(p.rating_text)}
                    <span>· ${escapeHTML(p.review_count_text)}</span>
                </p>
                <p class="availability">${escapeHTML(p.availability)}</p>
                <p class="brand">${escapeHTML(p.brand)}</p>
            </div>
        </article>
    `).join("");
}

async function loadProducts() {
    if (!mount || !count || !search) {
        console.error(
            "Orbit Goods: Required catalogue elements are missing."
        );
        return;
    }

    const apiPath = window.SMARTBUY_PRODUCTS_API;

    if (!apiPath) {
        count.textContent = "Catalogue configuration error";
        mount.innerHTML =
            '<p class="empty">The catalogue API URL was not configured.</p>';

        console.error(
            "Orbit Goods: SMARTBUY_PRODUCTS_API is undefined.",
            "Check the rendered HTML and body data-products-api attribute."
        );
        return;
    }

    mount.innerHTML = '<div class="loading">Loading catalogue…</div>';
    count.textContent = "Loading…";
    mount.setAttribute("aria-busy", "true");

    try {
        const apiUrl = new URL(apiPath, window.location.origin);
        apiUrl.searchParams.set("q", search.value.trim());

        console.log("Orbit Goods API request:", apiUrl.href);

        const response = await fetch(apiUrl);

        if (!response.ok) {
            throw new Error(
                `API returned HTTP ${response.status}: ${apiUrl.pathname}`
            );
        }

        const products = await response.json();

        if (!Array.isArray(products)) {
            throw new Error("API response was not a product array.");
        }

        render(products);
    } catch (error) {
        count.textContent = "Catalogue unavailable";
        mount.innerHTML =
            '<p class="empty">Could not load the catalogue. Check the browser console.</p>';

        console.error("Orbit Goods catalogue loading failed:", error);
    } finally {
        mount.setAttribute("aria-busy", "false");
    }
}

if (searchForm) {
    searchForm.addEventListener("submit", event => {
        event.preventDefault();
        loadProducts();
    });
}

document.querySelectorAll(".filter").forEach(button => {
    button.addEventListener("click", () => {
        activeCategory = button.dataset.category || "";

        document.querySelectorAll(".filter").forEach(filter => {
            filter.classList.toggle("active", filter === button);
        });

        loadProducts();
    });
});

loadProducts();