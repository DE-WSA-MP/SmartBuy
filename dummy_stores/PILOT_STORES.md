# SmartBuy Dummy Store Pilots

Two independent Flask pilots are included:
- Store 01 (Northstar Market): server-rendered HTML, port 5001.
- Store 05 (Orbit Goods): JavaScript-rendered catalogue, port 5005.

Both stores contain 18 synthetic listings drawn from the frozen assignment matrix. The public store datasets do not include canonical IDs.

## Prerequisites
Python 3.10+ and Flask installed in the active environment. The repository's existing `requirements.txt` may be used if Flask is installed there.

## Run Store 01
From `dummy_stores/store_01`:
```bash
python app.py
```
Open `http://127.0.0.1:5001`.

## Run Store 05
From `dummy_stores/store_05`:
```bash
python app.py
```
Open `http://127.0.0.1:5005`.

## Quick checks
- `http://127.0.0.1:5001/health`
- `http://127.0.0.1:5005/health`
- Store 05's initial HTML should not contain product titles; `/api/products` returns store-facing JSON without canonical IDs.
- All prices and ratings are synthetic test values, not live offers or current retail claims.

## Notes
The pilot apps intentionally have different visual styles, route implementation details, field presentation and rendering strategy. They are local testing fixtures, not production ecommerce systems.
