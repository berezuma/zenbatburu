#!/usr/bin/env python3
"""Orria muntatu: burua + gorputza + datuak + gidoia fitxategi bakarrean.

Irteera `index.html` da: GitHub Pages-ek hori bilatzen du erroan.

Partekatzeko etiketek URL absolutua behar dute, eta ostatu-helbidea
`SITE_URL` ingurune-aldagaitik hartzen da:

    SITE_URL=https://adibidea.eus/abereak python3 assemble.py

Hutsik badago, URL absolutua ezinbestean behar duten etiketak (`og:url`,
`canonical`) kendu egiten dira — okerreko URL bat baino hobe da bat ere ez.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "index.html")
BASE = os.environ.get("SITE_URL", "").rstrip("/")
OG = "zenbat-buru-og.png"


def read(name):
    with open(os.path.join(HERE, name)) as f:
        return f.read().rstrip() + "\n"


def urls(html):
    out = []
    for line in html.split("\n"):
        if "<!--abs-->" in line:
            if not BASE:
                continue
            line = line.replace("<!--abs-->", "")
        out.append(line)
    return "\n".join(out).replace("{{BASE}}/", BASE + "/" if BASE else "")


with open(os.path.join(HERE, "data", "abereak.json")) as f:
    data = f.read().strip()

page = (urls(read("page.head.html")) + "\n" + read("page.body.html") + "\n" +
        '<script type="application/json" id="ab-data">' + data + "</script>\n\n" +
        read("page.script.html"))

with open(OUT, "w") as f:
    f.write(page)

print(f"{os.path.relpath(OUT, HERE)}: {len(page):,} karaktere "
      f"({os.path.getsize(OUT) / 1024:,.0f} KB)")
print(f"oinarri-URLa    : {BASE or '(hutsik — og:url eta canonical kenduta)'}")

og = os.path.join(HERE, OG)
src = max(os.path.getmtime(os.path.join(HERE, f))
          for f in ("page.head.html", "page.body.html", "page.script.html"))
if not os.path.exists(og):
    print("partekatzeko txartela: FALTA DA — `node make-og.js`")
elif os.path.getmtime(og) < src:
    print("partekatzeko txartela: zaharkituta — `node make-og.js`")
else:
    print("partekatzeko txartela: eguneratuta")
