#!/usr/bin/env python3
import csv
import json
import time
from urllib.parse import quote
from urllib.request import Request, urlopen

AREAS = [
    "Elmhurst, Queens, New York, USA",
    "Cypress Hills, Brooklyn, New York, USA",
]

OVERPASS = "https://overpass-api.de/api/interpreter"
NOMINATIM = "https://nominatim.openstreetmap.org/search"


def http_get(url):
    req = Request(url, headers={"User-Agent": "ander-outreach-agent/1.0 (contact: ayalaander323@gmail.com)"})
    with urlopen(req, timeout=45) as r:
        return r.read().decode("utf-8")


def geocode_area(name):
    url = f"{NOMINATIM}?format=json&limit=1&q={quote(name)}"
    data = json.loads(http_get(url))
    if not data:
        return None
    item = data[0]
    return {
        "display": item.get("display_name", name),
        "lat": float(item["lat"]),
        "lon": float(item["lon"]),
    }


def overpass_nearby(lat, lon, radius=3500):
    query = f"""
[out:json][timeout:30];
(
  node(around:{radius},{lat},{lon})[shop];
  node(around:{radius},{lat},{lon})[amenity];
  way(around:{radius},{lat},{lon})[shop];
  way(around:{radius},{lat},{lon})[amenity];
  relation(around:{radius},{lat},{lon})[shop];
  relation(around:{radius},{lat},{lon})[amenity];
);
out center tags;
"""
    req = Request(OVERPASS, data=query.encode("utf-8"), headers={"User-Agent": "ander-outreach-agent/1.0"})
    with urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode("utf-8"))


def norm_email(text):
    if not text:
        return ""
    t = text.strip()
    if "@" in t and " " not in t and len(t) < 120:
        return t.replace("mailto:", "")
    return ""


def build_leads(max_leads=50):
    seen = set()
    leads = []

    for area in AREAS:
        g = geocode_area(area)
        if not g:
            continue
        time.sleep(1)
        data = overpass_nearby(g["lat"], g["lon"], radius=4000)
        for e in data.get("elements", []):
            tags = e.get("tags", {})
            name = tags.get("name", "").strip()
            if not name:
                continue

            website = tags.get("website") or tags.get("contact:website") or ""
            phone = tags.get("phone") or tags.get("contact:phone") or ""
            email = norm_email(tags.get("email") or tags.get("contact:email") or "")
            category = tags.get("shop") or tags.get("amenity") or "other"
            lat = e.get("lat") or (e.get("center") or {}).get("lat")
            lon = e.get("lon") or (e.get("center") or {}).get("lon")

            key = (name.lower(), str(lat), str(lon))
            if key in seen:
                continue
            seen.add(key)

            score = 50
            if website:
                score += 20
            if phone:
                score += 15
            if email:
                score += 15

            leads.append({
                "business_name": name,
                "area_hint": area,
                "category": category,
                "website": website,
                "email": email,
                "phone": phone,
                "lat": lat,
                "lon": lon,
                "score": min(score, 100),
                "source": "openstreetmap_overpass",
                "status": "new"
            })

    leads.sort(key=lambda x: (-x["score"], x["business_name"]))
    return leads[:max_leads]


def main():
    leads = build_leads(max_leads=50)
    out = "/home/ander/.openclaw/workspace/outreach_agent_v1/leads_50.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "business_name", "area_hint", "category", "website", "email", "phone",
            "lat", "lon", "score", "source", "status"
        ])
        w.writeheader()
        w.writerows(leads)
    print(f"wrote {out} rows={len(leads)}")


if __name__ == "__main__":
    main()
