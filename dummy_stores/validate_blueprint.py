#!/usr/bin/env python3
"""Validate the frozen SmartBuy dummy-store blueprint using only Python stdlib."""
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def read_csv(name):
    with (ROOT / name).open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

products = read_csv("master_catalog.csv")
assignments = read_csv("store_assignments.csv")
edges = read_csv("data_edge_cases.csv")

errors = []
product_ids = [r["canonical_id"] for r in products]
if len(products) != 30:
    errors.append(f"Expected 30 canonical products; found {len(products)}")
if len(set(product_ids)) != len(product_ids):
    errors.append("Duplicate canonical_id values found")
category_counts = Counter(r["category"] for r in products)
if len(category_counts) != 5:
    errors.append(f"Expected 5 categories; found {len(category_counts)}")
if any(n != 6 for n in category_counts.values()):
    errors.append(f"Expected 6 products/category; got {dict(category_counts)}")

if len(assignments) != 180:
    errors.append(f"Expected 180 assignments; found {len(assignments)}")
listing_keys = [(r["store_id"], r["listing_id"]) for r in assignments]
if len(set(listing_keys)) != len(listing_keys):
    errors.append("Duplicate (store_id, listing_id) assignment keys found")
unknown_canonical = sorted(set(r["canonical_id"] for r in assignments) - set(product_ids))
if unknown_canonical:
    errors.append(f"Assignments reference unknown canonical IDs: {unknown_canonical}")

store_counts = Counter(r["store_id"] for r in assignments)
if set(store_counts) != {f"S{i:02d}" for i in range(1, 11)}:
    errors.append(f"Expected stores S01–S10; got {sorted(store_counts)}")
if any(n != 18 for n in store_counts.values()):
    errors.append(f"Expected 18 listings/store; got {dict(store_counts)}")

product_coverage = Counter(r["canonical_id"] for r in assignments)
if set(product_coverage) != set(product_ids):
    errors.append("At least one canonical product has no store assignment")
if any(not 5 <= product_coverage[cid] <= 8 for cid in product_ids):
    errors.append(f"Product coverage outside 5–8 stores: {dict(product_coverage)}")
if any(product_coverage[cid] != 6 for cid in product_ids):
    errors.append(f"Blueprint v1 expects exactly 6 stores/product: {dict(product_coverage)}")

valid_listing_keys = set(listing_keys)
for edge in edges:
    key = (edge["store_id"], edge["listing_id"])
    if key not in valid_listing_keys:
        errors.append(f"Edge case {edge['test_case_id']} references unassigned listing {key}")

if errors:
    print("BLUEPRINT VALIDATION FAILED")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)

print("BLUEPRINT VALIDATION PASSED")
print(f"Canonical products: {len(products)}")
print(f"Categories: {len(category_counts)} -> {dict(category_counts)}")
print(f"Stores: {len(store_counts)} -> {dict(sorted(store_counts.items()))}")
print(f"Assignments: {len(assignments)}")
print(f"Coverage per canonical product: {min(product_coverage.values())}–{max(product_coverage.values())} stores")
print(f"Edge cases: {len(edges)}")
