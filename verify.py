#!/usr/bin/env python3
"""Orrian argitaratutako zifra bakoitza iturri gordinetik berriro kalkulatu.

`compact.py`-k sortutako fitxategia EZ da erabiltzen: dena `data/raw-*.json`-etik
berriro ateratzen da, bide independente batetik. Hala, trinkotzean akats bat
egonez gero, hemen agertuko da.

    python3 verify.py
"""
import json, os, re, sys, unicodedata
from collections import Counter, defaultdict

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
YEARS = ("2023", "2024", "2025")


def key(s):
    s = unicodedata.normalize("NFD", str(s or ""))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s).strip().upper()


def load(kind):
    with open(os.path.join(D, f"raw-{kind}.json")) as f:
        return json.load(f)["records"]


def g(r, name):
    for k in r:
        if k.split("/")[-1].strip() == name:
            v = r[k]
            return v.strip().lstrip("=").strip('"') if isinstance(v, str) else v
    raise KeyError(name)


# --- jaiotzak, bide independentea: multzo bat identifikazioekin
raw = load("jaiotzak")
seen, B = set(), []
for r in raw:
    if str(g(r, "EJERCICIO")) not in YEARS:
        continue
    aid = g(r, "IDENTIFICACION_ANIMAL")
    if aid in seen:
        continue
    seen.add(aid)
    B.append(r)

SP = {"BOVINOS": "behi", "OVINOS": "ardi", "CAPRINOS": "ahuntz",
      "CABALLO": "zaldi", "ASNO": "asto", "MULO": "mando"}
sp = [SP[key(g(r, "ESPECIE"))] for r in B]
yr = [str(g(r, "EJERCICIO")) for r in B]
fem = [key(g(r, "SEXO")).startswith("HEMBRA") for r in B]
dat = [str(g(r, "FECHA_NACIMIENTO"))[:10] for r in B]
raza = [key(g(r, "RAZA")) for r in B]

M = load("mugimenduak")
U = load("ustiategiak")

ok = bad = 0
def check(label, got, want, tol=0):
    global ok, bad
    good = abs(got - want) <= tol if isinstance(want, (int, float)) else got == want
    print(f"  {'OK  ' if good else 'HUTS'}  {label:52s} {got!r:>14}  (orrian: {want!r})")
    if good: ok += 1
    else: bad += 1


def by(pred):
    return sum(1 for i in range(len(B)) if pred(i))


print("JAIOTZAK")
check("animalia guztira", len(B), 84034)
for k, want in [("behi", 50194), ("ardi", 22122), ("ahuntz", 5644),
                ("zaldi", 5403), ("asto", 663), ("mando", 8)]:
    check(f"{k} guztira", by(lambda i, k=k: sp[i] == k), want)

print("\nSEXUA (emeen ehunekoa)")
for k, want in [("behi", 51.9), ("ardi", 90.9), ("ahuntz", 87.5)]:
    n = by(lambda i, k=k: sp[i] == k)
    f = by(lambda i, k=k: sp[i] == k and fem[i])
    check(f"{k} emeak %", round(100 * f / n, 1), want, 0.05)

print("\nHILAREN LEHEN EGUNA")
one = by(lambda i: dat[i][8:] == "01")
check("hilaren 1ean guztira", one, 13521)
check("hilaren 1ean %", round(100 * one / len(B), 1), 16.1, 0.05)
for k, want in [("ardi", 38.6), ("ahuntz", 38.0), ("behi", 4.5)]:
    n = by(lambda i, k=k: sp[i] == k)
    o = by(lambda i, k=k: sp[i] == k and dat[i][8:] == "01")
    check(f"{k} hilaren 1ean %", round(100 * o / n, 1), want, 0.05)

print("\nURTEZ URTE")
per = Counter(yr)
check("2023", per["2023"], 29619)
check("2025", per["2025"], 26077)
check("jaitsiera osoa %", round(100 * (per["2025"] - per["2023"]) / per["2023"]), -12)
for k, want in [("behi", 0), ("ardi", -28), ("ahuntz", -43), ("asto", -33)]:
    a = by(lambda i, k=k: sp[i] == k and yr[i] == "2023")
    b = by(lambda i, k=k: sp[i] == k and yr[i] == "2025")
    check(f"{k} 2023→2025 %", round(100 * (b - a) / a), want, 1)
check("behi 2023", by(lambda i: sp[i] == "behi" and yr[i] == "2023"), 16888)
check("behi 2025", by(lambda i: sp[i] == "behi" and yr[i] == "2025"), 16795)

print("\nURTAROAK (hilabetea fidagarria da, eguna ez)")
mon = [int(d[5:7]) for d in dat]
ardi_12 = by(lambda i: sp[i] == "ardi" and mon[i] in (1, 2))
check("arkumeak urt+ots %", round(100 * ardi_12 / by(lambda i: sp[i] == "ardi"), 1), 58.3, 0.05)
zaldi_45 = by(lambda i: sp[i] == "zaldi" and mon[i] in (4, 5))
check("moxalak api+mai %", round(100 * zaldi_45 / by(lambda i: sp[i] == "zaldi"), 1), 60.8, 0.05)
z1 = by(lambda i: sp[i] == "zaldi" and mon[i] == 1)
z4 = by(lambda i: sp[i] == "zaldi" and mon[i] == 4)
check("moxalak: apirila / urtarrila", round(z4 / z1), 23, 0)
check("moxalak urtarrilean", z1, 74)
check("moxalak apirilean", z4, 1709)

print("\nARRAZAK (81/2015 Dekretua)")
def fam(pre):
    return [i for i in range(len(B)) if raza[i].startswith(pre)]
def per_year(idx):
    c = Counter(yr[i] for i in idx)
    return [c["2023"], c["2024"], c["2025"]]
check("betizu guztira", len(fam("BETIZU")), 117)
check("betizu urtez", per_year(fam("BETIZU")), [41, 34, 42])
check("azpigorri 2023→2025", per_year(fam("AZPI GORRI"))[::2], [698, 337])
check("sasi ardi 2023→2025", per_year(fam("SASI ARDI"))[::2], [827, 546])
carr = fam("CARRANZANA"); check("carranzana 2023→2025", per_year(carr)[::2], [1309, 976])
check("monchina 2023→2025", per_year(fam("MONCHINA"))[::2], [348, 440])
check("terrena 2023→2025", per_year(fam("TERRENA"))[::2], [639, 795])
check("pottoka 2023→2025", per_year(fam("POTTOKA"))[::2], [96, 174])
check("mendiko zaldia 2023→2025", per_year(fam("CABALLO DE MONTE"))[::2], [316, 557])
check("enkarterriko astoa", len(fam("ASNO DE LAS ENCARTACIONES")), 185)
check("pottoka guztira", len(fam("POTTOKA")), 428)
mest = [i for i in range(len(B)) if raza[i].startswith("CONJUNTO MESTIZO")
        or raza[i].startswith("MESTIZO")]
check("mestizoak", len(mest), 31868)
check("euskal txerria / oiloa / antzara",
      len(fam("EUSKAL")), 0)

print("\nMUGIMENDUAK")
n = lambda r: int(g(r, "NUMERO_ANIMALES") or 0)
check("gidak", len(M), 63809)
check("abereak", sum(n(r) for r in M), 4708071)
check("gida handiena", max(n(r) for r in M), 35840)
nav = [r for r in M if g(r, "LUGAR_DESTINO") == "Navarra"]
check("Nafarroa: abereak", sum(n(r) for r in nav), 1092564)
check("Nafarroa: gidak", len(nav), 2832)
oilo = sorted(n(r) for r in M if key(g(r, "ESPECIE")) == "GALLINAS")
check("oiloen mediana", oilo[len(oilo) // 2], 3250)
for k, want in [("OVINOS", 65), ("CABALLO+EQUIDOS", 64), ("CAPRINOS", 59)]:
    ks = ["CABALLO", "EQUIDOS"] if "+" in k else [k]
    tot = sum(n(r) for r in M if key(g(r, "ESPECIE")) in ks)
    tr = sum(n(r) for r in M if key(g(r, "ESPECIE")) in ks and g(r, "TRASHUMANCIA") == "S")
    check(f"transhumantzia {k} %", round(100 * tr / tot), want, 1)

print("\nUSTIATEGIAK")
check("ilarak guztira", len(U), 52488)
check("2025eko ilarak", sum(1 for r in U if str(g(r, "EJERCICIO")) == "2025"), 10990)

print(f"\n{ok} ondo · {bad} huts")
sys.exit(1 if bad else 0)
