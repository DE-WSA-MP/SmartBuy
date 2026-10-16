from pathlib import Path
import importlib.util

from flask import Flask, render_template_string
from werkzeug.middleware.dispatcher import DispatcherMiddleware

ROOT = Path(__file__).resolve().parent
STORES = ROOT / "dummy_stores"

directory = Flask("store_directory")

STORE_PREFIXES = {
    "store_01": "/store01",
    "store_02": "/store02",
    "store_03": "/store03",
    "store_04": "/store04",
    "store_05": "/store05",
    "store_06": "/store06",
    "store_07": "/store07",
    "store_08": "/store08",
    "store_09": "/store09",
    "store_10": "/store10",
}


@directory.get("/")
def home():
    links = []

    for folder, prefix in STORE_PREFIXES.items():
        exists = (STORES / folder / "app.py").is_file()
        status = "Ready" if exists else "Not built yet"

        links.append(
            f'<li><a href="{prefix}/">{folder}</a> — {status}</li>'
        )

    return render_template_string("""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>SmartBuy Dummy Stores</title>
      </head>
      <body>
        <h1>SmartBuy Dummy Stores</h1>
        <ul>{{ links|safe }}</ul>
      </body>
    </html>
    """, links="".join(links))


mounted_apps = {}

for folder, prefix in STORE_PREFIXES.items():
    app_path = STORES / folder / "app.py"

    # Allow deployment while stores are being built incrementally.
    if not app_path.is_file():
        continue
    
    spec = importlib.util.spec_from_file_location(
        f"smartbuy_{folder}", app_path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    store_app = module.app
    store_root = app_path.parent.resolve()

    # Ensure this store uses its own templates and static assets.
    store_app.root_path = str(store_root)
    store_app.template_folder = str(store_root / "templates")

    store_static = store_root / "static"
    if store_static.is_dir():
        store_app.static_folder = str(store_static)

    mounted_apps[prefix] = store_app



app = DispatcherMiddleware(directory, mounted_apps)
