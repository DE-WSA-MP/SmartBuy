# SmartBuy Dummy Store Blueprint v1.0

## Frozen decisions
- 30 canonical products across 5 categories (6 per category)
- 10 independent Flask applications
- Each canonical product assigned to 6 stores (within target range 5–8)
- 18 listings per store; 180 assigned listings total
- 3 JavaScript-rendered stores: S05, S08, S10
- INR only
- Existing SmartBuy app remains separate and is not modified by this blueprint package

## Files
- `master_catalog.csv`: internal ground-truth canonical catalogue
- `store_assignments.csv`: 180 store/listing-to-canonical assignments
- `store_matrix.md`: store-specific data presentation and rendering profiles
- `data_edge_cases.csv`: planned normalization, availability, rendering, and matching cases
- `validate_blueprint.py`: standard-library validation script

## Important identity rule
`canonical_id` is internal ground truth. Do not copy it into public store pages, HTML data attributes, URLs, or public JSON responses. Each public listing should have a store-specific listing ID and a store-specific title.

## Validation
From this directory run:

```bash
python validate_blueprint.py
```

Expected high-level counts: 30 canonical products, 5 categories, 180 assignments, 18 listings per store, and 6 store appearances per canonical product.

## Independent application plan
Create `store_01` through `store_10`, each with its own `app.py`, `data/products.csv`, `templates/`, and `static/`. Use ports 5001–5010 respectively; the existing SmartBuy app retains port 5000.

## Data semantics
- All data is synthetic and intended for local development/testing.
- Use numeric INR values internally; preserve raw displayed strings.
- Keep selling price and MRP separate.
- Normalize ratings only when their scale and semantics are documented.
- Do not treat satisfaction percentages as star ratings by default.
- Preserve missing fields as missing.
- Keep unknown, out-of-stock, low-stock, pre-order, backorder, and discontinued states distinct.
