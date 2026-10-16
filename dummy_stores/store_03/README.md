# Store 03 — Signal Supply

Independent Flask storefront for SmartBuy dummy-store testing.

- Categories: Laptops, Audio, Wearables
- Listings: 18 (six per category)
- Local port: 5003
- Routes: `/`, `/health`, `/search` is not separately defined; use homepage search query `/?q=...`, `/category/<category>`, `/product/<slug>`
- All prices, ratings, reviews and availability are synthetic test data.
- Canonical IDs are intentionally omitted from public listing data.

Run from the SmartBuy project root: `python .\dummy_stores\store_03\app.py`
