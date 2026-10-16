# Store 09 — GOODFORM

Independent server-rendered Flask storefront for SmartBuy dummy-store testing.

- Store ID: S09
- Local port: 5009
- Categories: Laptops, Audio, Small home appliances
- Listings: 18 (six per category)
- Currency: INR
- Synthetic prices, list prices, ratings, reviews, and availability.
- Canonical product IDs are intentionally excluded from public listing data.

## Run standalone
From the SmartBuy project root:

```powershell
python .\\dummy_stores\\store_09\\app.py
```

Open `http://127.0.0.1:5009/` and `http://127.0.0.1:5009/health`.
Category pages: `/category/Laptops`, `/category/Audio`, `/category/Small%20home%20appliances`.
Search is available in the homepage search box. Product details use `/product/<slug>`.

## Combined app
Stop standalone server, launch the combined `render_app.py` using the established Werkzeug `run_simple` command, then open `/store09/` and `/store09/health` on port 8000.
