# Store 10 — ODD / EVEN

Final independent Flask storefront for SmartBuy dummy-store testing.

- Store ID: S10
- Local port: 5010
- Categories: Smartphones, Wearables, Small home appliances
- Listings: 18 (six per category)
- Rendering: server-rendered Flask/Jinja
- Distinct art direction: bold cobalt editorial index, yellow/red geometric graphics, typographic catalogue rows (not the repeated three-column product-card layout).
- Price values are plausible India-market reference estimates anchored to known retail price points for the exact model/variant where possible. These are not live offers and can vary by seller/date. Ratings, review counts and stock statuses are synthetic.
- Public CSV intentionally excludes canonical IDs.

## Run standalone
From SmartBuy project root:

```powershell
python .\\dummy_stores\\store_10\\app.py
```

Open `http://127.0.0.1:5010/` and `http://127.0.0.1:5010/health`.
Category routes: `/category/Smartphones`, `/category/Wearables`, `/category/Small%20home%20appliances`.
Search is available on the homepage; product details use `/product/<slug>`.

## Combined app
Stop standalone server and launch `render_app.py` using the established Werkzeug `run_simple` command. Open `/store10/` and `/store10/health` on port 8000.

## Price reference notes
The listed numbers are demo-store anchors, not a claim of live current availability. Example reference points include Samsung India's Galaxy S25 256GB listing (₹84,999), Philips India's NA231 air fryer (₹9,999), Apple Watch Series 10 42mm GPS price reference (about ₹30,999), and Eureka Forbes Robo Vac N Mop Pro (₹13,499). Prices can change; check official seller pages for current live prices.
