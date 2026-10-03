#!/usr/bin/env python3
"""Parse every JSON-LD block in site/**/*.html and fail if any is invalid or missing required keys.
Cheap guard so a typo in data/*.json never ships broken structured data."""
import json, re, sys
from pathlib import Path

REQUIRED = {
    "MusicEvent": ["name", "startDate", "location", "performer"],
    "FAQPage": ["mainEntity"],
    "BreadcrumbList": ["itemListElement"],
    "WebSite": ["name", "url"],
}
site = Path(__file__).resolve().parents[1] / "site"
bad = 0; total = 0
for f in sorted(site.rglob("*.html")):
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', f.read_text(encoding="utf-8"), re.S)
    for b in blocks:
        total += 1
        try:
            o = json.loads(b)
        except json.JSONDecodeError as e:
            print(f"INVALID JSON in {f}: {e}"); bad += 1; continue
        t = o.get("@type"); t = t if isinstance(t, list) else [t]
        if "Person" in t and not o.get("name"): print(f"{f}: Person missing name"); bad += 1
        for typ in t:
            for k in REQUIRED.get(typ, []):
                if k not in o: print(f"{f}: {typ} missing {k}"); bad += 1
print(f"{total} JSON-LD blocks checked, {bad} problem(s)")
sys.exit(1 if bad else 0)
