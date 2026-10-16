(() => {
  const search = document.getElementById("store-search");
  const cards = [...document.querySelectorAll(".store-card")];
  const filters = [...document.querySelectorAll(".filter-button")];
  const count = document.getElementById("result-count");
  const empty = document.getElementById("empty-state");
  let activeFilter = "all";

  function update() {
    const term = search.value.trim().toLowerCase();
    let visible = 0;
    cards.forEach(card => {
      const matchesText = !term || card.dataset.name.includes(term) || card.dataset.categories.includes(term);
      const matchesStatus = activeFilter === "all" || card.dataset.status === activeFilter;
      const show = matchesText && matchesStatus;
      card.hidden = !show;
      if (show) visible++;
    });
    count.textContent = `${String(visible).padStart(2, "0")} STORE${visible === 1 ? "" : "S"}`;
    empty.hidden = visible !== 0;
  }

  search.addEventListener("input", update);
  filters.forEach(button => button.addEventListener("click", () => {
    activeFilter = button.dataset.filter;
    filters.forEach(item => item.classList.toggle("active", item === button));
    update();
  }));
  document.addEventListener("keydown", event => {
    if (event.key === "/" && !["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)) {
      event.preventDefault();
      search.focus();
    }
    if (event.key === "Escape" && document.activeElement === search) {
      search.value = "";
      search.blur();
      update();
    }
  });
  update();
})();