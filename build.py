#!/usr/bin/env python3
"""Abeltzaintzako erregistroak jaitsi: ustiategiak, jaiotzak eta mugimenduak.

Iturria: Open Data Bizkaia, `explotaciones-ganaderas` datu-multzoa, CKAN
datastore APIaren bidez. Hiru taula-mota daude pakete berean, fitxategi-izenak
bereizten dituenak:

  DFBExplotacionesGanaderas  ustiategien erregistroa (urteko argazki bat)
  DFBNacimientosGanado       jaiotza bakoitza ilara bat
  DFBMovimientosGanado       abere-mugimenduen gida bakoitza ilara bat

Oharra: atariaren suebakiak `Mozilla/5.0` User-Agenta ukatzen du eta HTML bat
itzultzen du JSONaren ordez. Python-en lehenetsia onartzen du.
"""
import json, os, re, sys, urllib.request

API = "https://www.opendatabizkaia.eus/es/api/3/action"
HERE = os.path.dirname(os.path.abspath(__file__))
DATASET = "explotaciones-ganaderas"
PAGE = 10000

KIND = {
    "DFBExplotacionesGanaderas": "ustiategiak",
    "DFBNacimientosGanado": "jaiotzak",
    "DFBMovimientosGanado": "mugimenduak",
}


def get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=180) as r:
                return json.load(r)
        except Exception as e:
            if i == tries - 1:
                raise
            print(f"  berriro saiatzen ({e})", file=sys.stderr)


def label(res):
    """Baliabidearen izena hiru hizkuntzatan etor daiteke; fitxategia nahi dugu."""
    n = res.get("name") or ""
    if isinstance(n, str) and n.strip().startswith("{"):
        try:
            n = json.loads(n).get("es") or ""
        except ValueError:
            pass
    if isinstance(n, dict):
        n = n.get("es") or ""
    return n or res["id"]


def rows(rid):
    out, fields, off = [], None, 0
    while True:
        r = get(f"{API}/datastore_search?resource_id={rid}"
                f"&limit={PAGE}&offset={off}")["result"]
        if fields is None:
            fields = [f["id"] for f in r["fields"] if f["id"] != "_id"]
        recs = r["records"]
        if not recs:
            break
        out += recs
        off += PAGE
        if off >= r.get("total", 0):
            break
    return fields, out


def fetch():
    pkg = get(f"{API}/package_show?id={DATASET}")["result"]
    tables = {}
    for res in pkg["resources"]:
        if not res.get("datastore_active"):
            continue
        name = label(res)
        kind = next((v for k, v in KIND.items() if name.startswith(k)), None)
        if kind is None:
            print(f"  ! ezezaguna: {name}", file=sys.stderr)
            continue
        fields, recs = rows(res["id"])
        yrs = sorted({str(r.get("EKITALDIA/EJERCICIO")) for r in recs})
        print(f"  {kind:12s} {name[:40]:42s} {len(recs):>7,}  "
              f"{','.join(y for y in yrs if y and y != 'None')}")
        t = tables.setdefault(kind, {"fields": fields, "records": []})
        t["records"] += recs
        # Eremuek bat egin behar dute urte batetik bestera; bestela jakin nahi dugu.
        if t["fields"] != fields:
            print(f"  ! eremuak aldatu dira {name}-n", file=sys.stderr)
    return tables


if __name__ == "__main__":
    tables = fetch()
    print()
    for kind, t in sorted(tables.items()):
        path = os.path.join(HERE, "data", f"raw-{kind}.json")
        with open(path, "w") as f:
            json.dump(t, f, ensure_ascii=False)
        print(f"{kind:12s} {len(t['records']):>8,} erregistro  "
              f"{len(t['fields']):>2} eremu  {os.path.getsize(path):>12,} byte")
