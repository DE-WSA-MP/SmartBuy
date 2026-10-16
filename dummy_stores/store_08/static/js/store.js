(() => {
  "use strict";
  const config = window.STORE_CONFIG || {};
  const grid = document.getElementById("productGrid");
  const searchInput = document.getElementById("searchInput");
  const sortSelect = document.getElementById("sortSelect");
  const resultCount = document.getElementById("resultCount");
  const sectionTitle = document.getElementById("sectionTitle");
  const noResults = document.getElementById("noResults");
  const filters = document.getElementById("filters");
  const savedCount = document.getElementById("savedCount");
  let products = [];
  let selectedCategory = config.initialCategory || "All";
  let saved = new Set();

  const esc = (value) => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const money = (value) => "₹" + Number(value || 0).toLocaleString("en-IN", {maximumFractionDigits:0});
  const slugUrl = (slug) => (config.productPrefix || "/product/__SLUG__").replace("__SLUG__", encodeURIComponent(slug));
  function filtered() {
    const q = searchInput.value.trim().toLocaleLowerCase();
    let list = products.filter(p => (selectedCategory === "All" || p.category.toLowerCase() === selectedCategory.toLowerCase()) &&
      (!q || [p.title,p.brand,p.category,p.model_text,p.variant_text].some(v => String(v || "").toLowerCase().includes(q))));
    switch (sortSelect.value) {
      case "price-low": list.sort((a,b) => Number(a.price_value_inr)-Number(b.price_value_inr)); break;
      case "price-high": list.sort((a,b) => Number(b.price_value_inr)-Number(a.price_value_inr)); break;
      case "rating": list.sort((a,b) => Number(b.rating_raw_value)-Number(a.rating_raw_value)); break;
      default: list.sort((a,b) => a.listing_id.localeCompare(b.listing_id));
    }
    return list;
  }
  function card(p, index) {
    const savedItem = saved.has(p.listing_id);
    const art = index % 6;
    const symbol = p.category === "Smartphones" ? "▯" : p.category === "Laptops" ? "▱" : "◖ ◗";
    const statusClass = p.availability_raw === "Out of Stock" ? "out" : p.availability_raw === "Limited Stock" ? "limited" : "";
    return `<article class="card"><a class="product-art art-${art}" href="${esc(slugUrl(p.product_slug))}"><span class="product-no">MONO / ${String(index+1).padStart(2,"0")}</span><span class="product-symbol">${symbol}</span><span class="category">${esc(p.category.toUpperCase())}</span><span class="arrow">↗</span></a><div class="card-info"><p class="brand">${esc(p.brand)} <span>/ ${esc(p.category)}</span></p><h3><a href="${esc(slugUrl(p.product_slug))}">${esc(p.title)}</a></h3><div class="price"><strong>${esc(p.price_text)}</strong><del>${money(p.mrp_value_inr)}</del><span class="discount">${esc(p.discount_percent)}% OFF</span></div><p class="rating"><span>★★★★★</span> <b>${esc(p.rating_text)}</b></p><p class="reviews">${esc(p.review_count_text)}</p><p class="stock ${statusClass}">${esc(p.availability_raw)}${p.stock_count ? ` · ${esc(p.stock_count)} units` : ""}</p><button class="save-button ${savedItem ? "saved" : ""}" data-save="${esc(p.listing_id)}" aria-pressed="${savedItem}">${savedItem ? "♥ SAVED" : "♡ SAVE ITEM"}</button></div></article>`;
  }
  function render() {
    const list = filtered();
    grid.innerHTML = list.map(card).join("");
    grid.hidden = list.length === 0;
    noResults.hidden = list.length !== 0;
    resultCount.textContent = `${String(list.length).padStart(2,"0")} ITEMS / ${products.length} TOTAL`;
    sectionTitle.textContent = selectedCategory === "All" ? (searchInput.value.trim() ? "Search results." : "The everyday edit.") : selectedCategory + ".";
    savedCount.textContent = saved.size;
    filters.querySelectorAll("button").forEach(b => {
      b.classList.toggle("active", b.dataset.category === selectedCategory);
      b.setAttribute("aria-pressed", String(b.dataset.category === selectedCategory));
    });
  }
  filters.addEventListener("click", e => {
    const button = e.target.closest("button[data-category]");
    if (!button) return;
    selectedCategory = button.dataset.category;
    render();
  });
  searchInput.addEventListener("input", render);
  sortSelect.addEventListener("change", render);
  grid.addEventListener("click", e => {
    const button = e.target.closest("button[data-save]");
    if (!button) return;
    const id = button.dataset.save;
    if (saved.has(id)) saved.delete(id); else saved.add(id);
    render();
  });
  document.getElementById("bagButton").addEventListener("click", () => {
    if (!saved.size) { window.alert("No saved items yet. Use ♡ SAVE ITEM on a product to add one."); return; }
    window.alert(`You have ${saved.size} saved item${saved.size === 1 ? "" : "s"} in this demo session.`);
  });
  fetch(config.apiUrl || "/api/products")
    .then(response => { if (!response.ok) throw new Error("Could not load product data."); return response.json(); })
    .then(data => {
      products = Array.isArray(data.products) ? data.products : [];
      if (config.initialCategory && !products.some(p => p.category.toLowerCase() === config.initialCategory.toLowerCase())) selectedCategory = "All";
      render();
    })
    .catch(() => {
      grid.innerHTML = "";
      grid.hidden = true;
      noResults.hidden = false;
      noResults.textContent = "The collection could not load. Please refresh and try again.";
      resultCount.textContent = "COLLECTION UNAVAILABLE";
    });
})();