# Store 04 — HomeGrid

HomeGrid is an independent Flask demo storefront for the SmartBuy dummy-store project. It has a warm cream, terracotta and natural-material visual identity.

- Store ID: `S04`
- Local port: `5004`
- Categories: Smartphones, Laptops, Small home appliances
- Listings: 18 (6 per category)
- Rendering: server-rendered Flask/Jinja templates
- Currency: INR

All prices, ratings, review counts and availability values are synthetic test data. The public listing CSV and pages intentionally omit canonical product IDs.

## Run independently
From the SmartBuy project root:

```powershell
python .\dummy_stores\store_04\app.py
```

Open `http://127.0.0.1:5004/` and `http://127.0.0.1:5004/health`. Category routes are `/category/Smartphones`, `/category/Laptops`, and `/category/Small%20home%20appliances`. Product pages use `/product/<slug>`. Search is available from the homepage search field.

## Combined app
With the standalone server stopped, run the combined `render_app.py` using the same Werkzeug `run_simple` approach as the other stores, then open `/store04/` and `/store04/health` on port 8000.
