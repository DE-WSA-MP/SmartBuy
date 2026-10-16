# Store 07 — FIELDWORK

Independent Flask demo storefront for the SmartBuy dummy-store project.

- Store ID: `S07`
- Local port: `5007`
- Categories: Laptops, Wearables, Small home appliances
- Listings: 18 (six per category)
- Rendering: server-rendered Flask/Jinja
- Currency: INR
- All prices, ratings, review counts and availability are synthetic.
- Public listing data intentionally excludes canonical product IDs.

## Run independently
From the SmartBuy project root:

```powershell
python .\\dummy_stores\\store_07\\app.py
```

Open `http://127.0.0.1:5007/` and `http://127.0.0.1:5007/health`.
Category routes: `/category/Laptops`, `/category/Wearables`, `/category/Small%20home%20appliances`.
Search is available on the homepage. Product pages use `/product/<slug>`.

## Combined app
Stop the standalone server, start the combined `render_app.py` with the existing Werkzeug `run_simple` launcher, and open `/store07/` and `/store07/health` on port 8000.
