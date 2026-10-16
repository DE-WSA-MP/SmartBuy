# Store 06 — Pulse & Co.

Independent Flask demo storefront for the SmartBuy dummy-store project.

- Store ID: `S06`
- Local port: `5006`
- Categories: Smartphones, Audio, Wearables
- Listings: 18 (6 per category)
- Rendering: server-rendered Flask/Jinja templates
- Currency: INR
- Price representation: separate selling price and list price, with discount badge
- Availability values: `Pre-order`, `In Stock`, `Out of Stock`

All prices, ratings, review counts and availability values are synthetic test data. Public pages and product CSV intentionally omit canonical product IDs.

## Run independently
From the SmartBuy project root:

```powershell
python .\\dummy_stores\\store_06\\app.py
```

Open `http://127.0.0.1:5006/` and `http://127.0.0.1:5006/health`. Category routes are `/category/Smartphones`, `/category/Audio`, and `/category/Wearables`. Product pages use `/product/<slug>`. Search is available from the homepage search field.

## Combined app
With the standalone server stopped, run the combined `render_app.py` using the existing Werkzeug `run_simple` approach, then open `/store06/` and `/store06/health` on port 8000.
