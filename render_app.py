from pathlib import Path
import importlib.util

from flask import Flask, render_template
from werkzeug.middleware.dispatcher import DispatcherMiddleware

ROOT = Path(__file__).resolve().parent
STORES = ROOT / "dummy_stores"

directory = Flask(
    "store_directory",
    template_folder=str(ROOT / "templates"),
    static_folder=str(ROOT / "static"),
)

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

STORE_DETAILS = {
    "store_01": {"name": "Northstar Market", "tagline": "Everyday tech, clearly chosen.", "categories": "Smartphones · Laptops · Audio", "port": 5001, "style": "northstar", "number": "01"},
    "store_02": {"name": "Fern & Form", "tagline": "Considered essentials for daily life.", "categories": "Smartphones · Wearables · Home", "port": 5002, "style": "fern", "number": "02"},
    "store_03": {"name": "Signal Supply", "tagline": "High signal. Zero noise.", "categories": "Laptops · Audio · Wearables", "port": 5003, "style": "signal", "number": "03"},
    "store_04": {"name": "HomeGrid", "tagline": "Make room for better routines.", "categories": "Home · Kitchen · Personal care", "port": 5004, "style": "homegrid", "number": "04"},
    "store_05": {"name": "Orbit Goods", "tagline": "Good things, in your orbit.", "categories": "Audio · Wearables · Home", "port": 5005, "style": "orbit", "number": "05"},
    "store_06": {"name": "Store 06", "tagline": "A separate storefront, ready to explore.", "categories": "3 categories · 18 listings", "port": 5006, "style": "store6", "number": "06"},
    "store_07": {"name": "FIELDWORK", "tagline": "Useful by design. Ready for real life.", "categories": "Laptops · Wearables · Home", "port": 5007, "style": "fieldwork", "number": "07"},
    "store_08": {"name": "MONOCHROME", "tagline": "Less noise. More product.", "categories": "Smartphones · Laptops · Audio", "port": 5008, "style": "mono", "number": "08"},
    "store_09": {"name": "GOODFORM", "tagline": "Well-made choices for everyday use.", "categories": "Laptops · Audio · Home", "port": 5009, "style": "goodform", "number": "09"},
    "store_10": {"name": "ODD / EVEN", "tagline": "A different kind of product index.", "categories": "Smartphones · Wearables · Home", "port": 5010, "style": "oddeven", "number": "10"},
}


@directory.get("/")
def home():
    stores = []
    for folder, prefix in STORE_PREFIXES.items():
        app_path = STORES / folder / "app.py"
        details = STORE_DETAILS[folder].copy()
        details["prefix"] = prefix
        details["exists"] = app_path.is_file()
        details["status"] = "Ready" if details["exists"] else "Not installed"
        stores.append(details)

    ready_count = sum(1 for store in stores if store["exists"])
    return render_template("hub.html", stores=stores, ready_count=ready_count)


mounted_apps = {}
for folder, prefix in STORE_PREFIXES.items():
    app_path = STORES / folder / "app.py"
    if not app_path.is_file():
        continue

    spec = importlib.util.spec_from_file_location(f"smartbuy_{folder}", app_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    store_app = module.app
    store_root = app_path.parent.resolve()
    store_app.root_path = str(store_root)
    store_app.template_folder = str(store_root / "templates")
    store_static = store_root / "static"
    if store_static.is_dir():
        store_app.static_folder = str(store_static)

    mounted_apps[prefix] = store_app

app = DispatcherMiddleware(directory, mounted_apps)
