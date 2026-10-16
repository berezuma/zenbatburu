#!/usr/bin/env python3
"""Hiru erregistro gordinak orriak jan dezakeen formatu trinkora pasatu.

Iturriak lau arazo ditu, eta laurak hemen konpontzen dira, dokumentatuta:

1. Excel moduan bildutako kodeak: `="022"`.
2. Espezieen izenak taula batetik bestera aldatzen dira: jaiotzetan «Bovinos»,
   ustiategietan «Bovidos»; «Caballo» eta «Asno» jaiotzetan, «Équidos»
   mugimenduetan.
3. Arrazen izenak maiuskulaz eta minuskulaz nahasten dira.
4. Arrazak batzuetan familia gisa etiketatzen dira («LATXA») eta batzuetan
   aldaera gisa («LATXA CARA NEGRA»), erregistratzailearen arabera. Aldaeren
   joera, beraz, ez da fidagarria: familia mailan neurtzen da dena, eta aldaerak
   informazio gisa gordetzen dira, ez serie gisa.

Jaiotzen taulan 2023–2025 urteak bakarrik hartzen dira: beste 13 erregistro
dago, 2008tik 2026ra sakabanatuta, eta urte horiek ez daude osorik.

Arrazen egoera ofiziala **81/2015 Dekretuaren eranskinetik** dator (EHAA 110,
2015-06-15, Euskal Arraza Autoktonoen Katalogo Ofiziala). Ez da guk emandako
sailkapena.

Irteera: data/abereak.json
"""
import base64, json, os, re, struct, unicodedata
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "data")
YEARS = (2023, 2024, 2025)
EXCEL = re.compile(r'^="?(.*?)"?$')


def unwrap(v):
    if isinstance(v, str):
        m = EXCEL.match(v.strip())
        return m.group(1) if m else v.strip()
    return v


def key(s):
    s = unicodedata.normalize("NFD", str(s or ""))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s).strip().upper()


SPECIES = {
    "BOVINOS": "behi", "BOVIDOS": "behi",
    "OVINOS": "ardi", "OVINO": "ardi",
    "CAPRINOS": "ahuntz", "CAPRINO": "ahuntz",
    "CABALLO": "zaldi", "EQUIDOS": "zaldi",
    "ASNO": "asto", "MULO": "mando", "BURDEGANO": "mando",
    "CERDOS": "txerri", "GALLINAS": "oilo", "CONEJOS": "untxi",
    "ABEJAS": "erle", "PATOS": "ahate", "OCAS": "antzara",
    "PALOMAS": "uso", "PAVOS": "indioilar", "RATITES": "ratite",
    "JABALIES": "basurde", "TORTUGAS (CHELONIA)": "dortoka",
}
SP_ORDER = ["behi", "ardi", "ahuntz", "zaldi", "asto", "mando"]
SP_EU = {"behi": "Behiak", "ardi": "Ardiak", "ahuntz": "Ahuntzak",
         "zaldi": "Zaldiak", "asto": "Astoak", "mando": "Mandoak",
         "txerri": "Txerriak", "oilo": "Oiloak", "untxi": "Untxiak",
         "erle": "Erleak", "ahate": "Ahateak", "antzara": "Antzarak",
         "uso": "Usoak", "indioilar": "Indioilarrak", "ratite": "Ratiteak",
         "basurde": "Basurdeak", "dortoka": "Dortokak"}
SP_ES = {"behi": "Bovinos", "ardi": "Ovinos", "ahuntz": "Caprinos",
         "zaldi": "Equinos", "asto": "Asnos", "mando": "Mulos",
         "txerri": "Cerdos", "oilo": "Gallinas", "untxi": "Conejos",
         "erle": "Abejas", "ahate": "Patos", "antzara": "Ocas",
         "uso": "Palomas", "indioilar": "Pavos", "ratite": "Ratites",
         "basurde": "Jabalíes", "dortoka": "Tortugas"}

# Arraza-familiak. Aurrizkia → familiaren izena. Ordena garrantzitsua da:
# luzeena lehenik, «CARRANZANA CARA NEGRA» «CARRANZANA» baino lehen begira dezan.
FAMILY = [
    ("CONJUNTO MESTIZO", "Mestizoak"), ("MESTIZO DE PONI", "Mestizoak"),
    ("MESTIZO", "Mestizoak"),
    ("LATXA", "Latxa"), ("CARRANZANA", "Carranzana"), ("SASI ARDI", "Sasi Ardi"),
    ("TERRENA", "Terreña"), ("MONCHINA", "Monchina"), ("BETIZU", "Betizu"),
    ("PIRENAICA", "Pirenaica"), ("AZPI GORRI", "Azpigorri"),
    ("AZPIGORRI", "Azpigorri"), ("POTTOKA", "Pottoka"),
    ("CABALLO DE MONTE", "Euskal Herriko Mendiko Zaldia"),
    ("ASNO DE LAS ENCARTACIONES", "Enkarterriko astoa"),
    ("EUSKAL TXERRIA", "Euskal Txerria"), ("EUSKAL OILOA", "Euskal Oiloa"),
    ("EUSKAL ANTZARA", "Euskal Antzara"),
    ("ASTURIANA", "Asturiana"), ("PARDA", "Parda"),
]

# 81/2015 Dekretuaren eranskina: familia → (espeziea, egoera ofiziala).
# Aldaerak bereiz zerrendatzen ditu dekretuak; familia mailan egoera
# zorrotzena gordetzen da, eta aldaeren xehetasuna testuan azaltzen da.
DEC81 = {
    "Betizu": ("behi", "En peligro"),
    "Monchina": ("behi", "Crítica"),
    "Pirenaica": ("behi", "No en riesgo"),
    "Terreña": ("behi", "En peligro"),
    "Carranzana": ("ardi", "En peligro"),      # Cara Negra: en peligro; Cara Rubia: no en riesgo
    "Latxa": ("ardi", "No en riesgo"),         # bi aldaerak: no en riesgo
    "Sasi Ardi": ("ardi", "En peligro"),
    "Azpigorri": ("ahuntz", "Crítica"),
    "Euskal Txerria": ("txerri", "Crítica"),
    "Euskal Herriko Mendiko Zaldia": ("zaldi", "En peligro"),
    "Pottoka": ("zaldi", "En peligro"),
    "Enkarterriko astoa": ("asto", "Crítica"),
    "Euskal Antzara": ("antzara", "Crítica"),
    "Euskal Oiloa": ("oilo", "Crítica"),
}


def nice(s):
    s = re.sub(r"\s+", " ", str(s or "").strip())
    if not s or s.upper() != s:
        return s
    return s.capitalize()


def family(raza):
    k = key(raza)
    for pre, name in FAMILY:
        if k.startswith(pre):
            return name
    return nice(raza)


def load(kind):
    with open(os.path.join(D, f"raw-{kind}.json")) as f:
        return json.load(f)["records"]


def fld(r, name):
    """Eremuak «EUSKARA/CASTELLANO» datoz. Gaztelaniazko erdia zehatz bilatzen
    da: `in` erabiltzeak CODIGO_LUGAR_DESTINO hartuko luke LUGAR_DESTINO-ren
    ordez, eta kodea itzuliko luke izenaren ordez."""
    for k in r:
        if k.split("/")[-1].strip() == name or k == name:
            return unwrap(r[k])
    raise KeyError(name)


def doy(date):
    """Urteko eguna, 0tik. Otsailaren 29a 59 da beti, urte guztiak lerrokatuta."""
    y, m, d = int(date[:4]), int(date[5:7]), int(date[8:10])
    cum = (0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335)
    return cum[m - 1] + d - 1


# --------------------------------------------------------------- jaiotzak
def births():
    seen, out, dropped = set(), [], Counter()
    for r in load("jaiotzak"):
        y = int(fld(r, "EJERCICIO"))
        if y not in YEARS:
            dropped["urtea ez da osoa"] += 1
            continue
        aid = fld(r, "IDENTIFICACION_ANIMAL")
        if aid in seen:
            dropped["identifikazioa bikoiztua"] += 1
            continue
        seen.add(aid)
        sp = SPECIES.get(key(fld(r, "ESPECIE")))
        if sp is None:
            dropped["espezie ezezaguna"] += 1
            continue
        raza = fld(r, "RAZA")
        date = str(fld(r, "FECHA_NACIMIENTO"))[:10]
        out.append({
            "y": y, "d": doy(date), "dom": int(date[8:10]), "sp": sp,
            "sex": 0 if key(fld(r, "SEXO")).startswith("HEMBRA") else 1,
            "fam": family(raza), "raza": nice(raza),
            "mun": fld(r, "MUNICIPIO"),
            "farm": fld(r, "EXPLOTACION_NACIMIENTO"),
        })
    return out, dropped


def b64(arr, fmt):
    return base64.b64encode(struct.pack(f"<{len(arr)}{fmt}", *arr)).decode()


def main():
    B, dropped = births()
    B.sort(key=lambda a: (a["y"], a["d"]))

    # --- hiztegiak, maiztasunaren arabera ordenatuta
    fams = [f for f, _ in Counter(b["fam"] for b in B).most_common()]
    muns = [m for m, _ in Counter(b["mun"] for b in B).most_common()]
    fam_i = {f: i for i, f in enumerate(fams)}
    mun_i = {m: i for i, m in enumerate(muns)}
    assert len(fams) < 256 and len(muns) < 256

    # --- animalia bakoitza zenbaki bakarrean: eguna | urtea | espeziea | sexua
    W, FA, MU = [], [], []
    for b in B:
        W.append(b["d"] | (YEARS.index(b["y"]) << 9)
                 | (SP_ORDER.index(b["sp"]) << 11) | (b["sex"] << 14))
        FA.append(fam_i[b["fam"]])
        MU.append(mun_i[b["mun"]])

    # --- arraza-familien fitxak
    fam_rows = []
    for f in fams:
        rows = [b for b in B if b["fam"] == f]
        sp = Counter(b["sp"] for b in rows).most_common(1)[0][0]
        per = [sum(1 for b in rows if b["y"] == y) for y in YEARS]
        var = Counter(b["raza"] for b in rows)
        d = DEC81.get(f)
        fam_rows.append({
            "n": f, "sp": sp, "t": len(rows), "y": per,
            "f": sum(1 for b in rows if b["sex"] == 0),
            "v": [[k, v] for k, v in var.most_common()] if len(var) > 1 else [],
            "o": d[1] if d else None,
        })

    # --- katalogo ofiziala: zer ikusten du erregistroak eta zer ez
    official = []
    for name, (sp, st) in DEC81.items():
        row = next((r for r in fam_rows if r["n"] == name), None)
        official.append({"n": name, "sp": sp, "o": st,
                         "t": row["t"] if row else 0,
                         "y": row["y"] if row else [0, 0, 0]})

    # --- udalerriak
    mun_rows = []
    for m in muns:
        rows = [b for b in B if b["mun"] == m]
        mun_rows.append({"n": m, "t": len(rows),
                         "y": [sum(1 for b in rows if b["y"] == y) for y in YEARS],
                         "sp": [sum(1 for b in rows if b["sp"] == s) for s in SP_ORDER]})

    # --- espezieak: sexua, urtea, hilabetea
    sp_rows = []
    for s in SP_ORDER:
        rows = [b for b in B if b["sp"] == s]
        mon = [0] * 12
        for b in rows:
            cum = (0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335)
            mon[max(i for i in range(12) if cum[i] <= b["d"])] += 1
        sp_rows.append({"k": s, "eu": SP_EU[s], "es": SP_ES[s], "t": len(rows),
                        "f": sum(1 for b in rows if b["sex"] == 0),
                        "y": [sum(1 for b in rows if b["y"] == y) for y in YEARS],
                        "m": mon})

    # --- biribiltzea: hilaren zein egunetan dagoen idatzita jaiotza.
    # Iturriak sarritan ez daki eguna, eta hilaren 1a jartzen du. Ez da
    # akats bat guretzat: erregistroaren zehaztasuna da, eta esan egin behar da.
    dom = [0] * 32
    for b in B:
        dom[b["dom"]] += 1
    first = {s: [sum(1 for b in B if b["sp"] == s and b["dom"] == 1),
                 sum(1 for b in B if b["sp"] == s)] for s in SP_ORDER}
    round_ = {"dom": dom[1:], "sp": first,
              "one": sum(1 for b in B if b["dom"] == 1)}

    # --- ustiategiak: jaiotzak non
    farm = Counter(b["farm"] for b in B)
    fv = sorted(farm.values())

    out = {
        "years": list(YEARS),
        "n": len(B),
        "fams": fams, "muns": muns,
        "w": b64(W, "H"), "fa": b64(FA, "B"), "mu": b64(MU, "B"),
        "sp": sp_rows, "fam": fam_rows, "mun": mun_rows, "official": official,
        "round": round_,
        "farms": {"n": len(farm), "med": fv[len(fv) // 2], "max": max(fv),
                  "top": farm.most_common(1)[0][1]},
        "drop": dict(dropped),
        "move": moves(),
        "hold": holdings(),
    }
    path = os.path.join(D, "abereak.json")
    with open(path, "w") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    print(f"jaiotzak      {len(B):>8,} animalia  ({dict(dropped)})")
    print(f"arraza-fam.   {len(fams):>8}   udalerriak {len(muns)}")
    print(f"fitxategia    {os.path.getsize(path):>8,} byte")
    return out


# ------------------------------------------------------------ mugimenduak
def moves():
    R = load("mugimenduak")
    per_year, per_sp, dest, cat, sizes = (defaultdict(lambda: [0, 0]),
                                          defaultdict(lambda: [0, 0, 0]),
                                          defaultdict(lambda: [0, 0]),
                                          Counter(), defaultdict(list))
    for r in R:
        y = str(fld(r, "EJERCICIO"))
        n = int(fld(r, "NUMERO_ANIMALES") or 0)
        sp = SPECIES.get(key(fld(r, "ESPECIE")), "beste")
        tr = fld(r, "TRASHUMANCIA") == "S"
        o = fld(r, "MUNICIPIO_ORIGEN") not in ("", "NULL", None)
        d = fld(r, "MUNICIPIO_DESTINO") not in ("", "NULL", None)
        per_year[y][0] += 1
        per_year[y][1] += n
        s = per_sp[sp]
        s[0] += 1
        s[1] += n
        s[2] += n if tr else 0
        dd = dest[fld(r, "LUGAR_DESTINO") or "—"]
        dd[0] += 1
        dd[1] += n
        cat["barrukoa" if o and d else "irteera" if o else "sarrera" if d else "kanpokoa"] += 1
        sizes[sp].append(n)
    med = {}
    for k, v in sizes.items():
        v.sort()
        med[k] = v[len(v) // 2]
    return {
        "year": {k: v for k, v in sorted(per_year.items())},
        "sp": sorted(([k, v[0], v[1], v[2], med[k]] for k, v in per_sp.items()),
                     key=lambda x: -x[2]),
        "dest": sorted(([k, v[0], v[1]] for k, v in dest.items()),
                       key=lambda x: -x[2])[:12],
        "cat": dict(cat),
        "guides": len(R), "animals": sum(v[1] for v in per_year.values()),
    }


# ------------------------------------------------------------- ustiategiak
def holdings():
    R = load("ustiategiak")
    per = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    sust, syst = Counter(), Counter()
    for r in R:
        y = str(fld(r, "EJERCICIO"))
        sp = SPECIES.get(key(fld(r, "ESPECIE")), "beste")
        try:
            c = int(fld(r, "CENSO") or 0)
        except ValueError:
            c = 0
        per[sp][y][0] += 1
        per[sp][y][1] += c
        if y == "2025":
            sust[fld(r, "SOSTENIBILIDAD") or "—"] += 1
            syst[fld(r, "SISTEMA PRODUCTIVO") or "—"] += 1
    return {
        "sp": sorted(([s, {y: v for y, v in sorted(d.items())}] for s, d in per.items()),
                     key=lambda x: -x[1].get("2025", [0, 0])[0]),
        "sust": sust.most_common(), "syst": syst.most_common(),
        "rows": len(R),
    }


if __name__ == "__main__":
    main()
