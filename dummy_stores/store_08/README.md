# Store 08 — MONOCHROME

Independent JavaScript-rendered Flask demo storefront for SmartBuy.

- Store ID: `S08`
- Local port: `5008`
- Categories: Smartphones, Laptops, Audio
- Listings: 18 (six per category)
- Rendering: Flask serves the shell and `/api/products`; JavaScript fetches and renders product cards.
- Interactive category filters, search, sorting, and session-only saved-item toggles.
- Currency: INR.
- All prices, ratings, review counts and availability are synthetic. Public data intentionally excludes canonical IDs.

## Run independently
From the SmartBuy project root:

```powershell
python .\\dummy_stores\\store_08\\app.py
```

Open `http://127.0.0.1:5008/`, `http://127.0.0.1:5008/health`, and `http://127.0.0.1:5008/api/products`.
Category routes: `/category/Smartphones`, `/category/Laptops`, `/category/Audio`.

## Combined app
Stop the standalone server, launch `render_app.py` with the existing Werkzeug `run_simple` launcher, then open `/store08/` and `/store08/health` on port 8000.
