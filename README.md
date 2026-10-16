# SmartBuy Hub Polish

This package contains a polished directory hub for the existing combined Flask/DispatcherMiddleware app.

## Files
- `render_app.py` — updated combined app. Keep your current store mount structure and per-store template/static path setup.
- `templates/hub.html` — directory UI.
- `static/hub.css` — responsive styling and store-specific visual treatments.
- `static/hub.js` — client-side search and status filters.

## Install
Copy `render_app.py` to the SmartBuy project root, and copy `templates/hub.html`, `static/hub.css`, and `static/hub.js` into the corresponding folders at the same root. Back up your current `render_app.py` first. This patch does not modify individual stores or `render.yaml`.

The hub's cards are generated from `STORE_DETAILS` and the `STORE_PREFIXES` map. The status is determined by whether each `dummy_stores/store_XX/app.py` file exists.

## Run locally
Use the previously verified combined-app launcher in PowerShell:
```powershell
@'
from werkzeug.serving import run_simple
from render_app import app

run_simple("127.0.0.1", 8000, app, use_reloader=False)
'@ | python
```
Open `http://127.0.0.1:8000/`.

## Notes
- Store names/categories are labels in `STORE_DETAILS`; edit them to match any naming changes.
- This directory assumes all ten stores are planned to expose 18 listings each; the displayed 180 is the blueprint total, not a live API count.
- Google Fonts are loaded from Google Fonts; system fallbacks are specified.
