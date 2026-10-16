# Store 02 — Fern & Form

Independent Flask storefront for the SmartBuy dummy-store suite.

- Categories: Smartphones, Wearables, Small home appliances
- Listings: 18 (6 per category)
- Rendering: server-side Jinja templates
- Local port: 5002
- Combined mount: `/store02/`
- All product, rating, review and price fields are synthetic test data, not live retailer claims.
- Public product CSV and markup do not include canonical ground-truth IDs.

## Run from the repository root

```powershell
python .\dummy_stores\store_02\app.py
```

Open `http://127.0.0.1:5002/`. Health check: `http://127.0.0.1:5002/health`.
