"""Haalt de bronnen op die via internet beschikbaar zijn en bewaart ze in data/ruw/.

Los van pipeline.py: dit script gebruikt internet, de pipeline niet (rij 75).
Opnieuw ophalen (bv. als INE de telling van 1/1/2026 publiceert):

    conda activate syntra-ds
    python ophalen_bronnen.py

Bronnen:
- INE tabel 2856 "Alicante/Alacant: Población por municipios y sexo" (B4, rij 54)
- Wikidata: coördinaten van de kaartpunten (B7, rij 61-62)
"""
import csv
import json
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

RUW = Path(__file__).parent / "data" / "ruw"
USER_AGENT = "SyntraCursusProject/1.0 (studieproject Costa Blanca Zuid)"

INE_URL = "https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/2856?nult=8&tip=A"

# Kaartpunten (rij 61-62): centrum van de hoofdkern, behalve Elche en Orihuela = kustkern.
# Gemeentes worden gezocht via hun INE-code (Wikidata-eigenschap P772),
# de twee kustkernen via hun Wikidata-code.
KAARTPUNTEN = [
    # (ine_code, gemeente, kaartpunt, wikidata_kustkern of None)
    ("03065", "Elche", "Los Arenales del Sol (kustkern)", "Q9023882"),
    ("03133", "Torrevieja", "centrum", None),
    ("03121", "Santa Pola", "centrum", None),
    ("03099", "Orihuela", "Orihuela Costa (kustkern)", "Q2803214"),
    ("03076", "Guardamar del Segura", "centrum", None),
    ("03902", "Pilar de la Horadada", "centrum", None),
]


def _get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def ophalen_ine():
    """Bewaart alle reeksen van tabel 2856 (alle gemeentes, totaal/mannen/vrouwen, 8 jaar)."""
    data = _get_json(INE_URL)
    pad = RUW / "ine_2856_inwoners.csv"
    with pad.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["reeks", "jaar", "datum", "waarde", "opgehaald"])
        n = 0
        for reeks in data:
            for punt in reeks["Data"]:
                w.writerow([reeks["Nombre"].strip(), punt["Anyo"], punt["Fecha"][:10], punt["Valor"], date.today().isoformat()])
                n += 1
    print(f"INE: {len(data)} reeksen, {n} rijen -> {pad}")


WIKIDATA_API = "https://www.wikidata.org/w/api.php?"


def _wikidata(params):
    """Gewone Wikidata-API (niet de SPARQL-dienst, die soms overbelast is)."""
    return _get_json(WIKIDATA_API + urllib.parse.urlencode({**params, "format": "json"}))


def _item_voor_ine_code(ine_code):
    """Zoekt het Wikidata-item met INE-gemeentecode (eigenschap P772) = ine_code."""
    res = _wikidata({"action": "query", "list": "search", "srsearch": f"haswbstatement:P772={ine_code}"})
    treffers = [t["title"] for t in res["query"]["search"]]
    if len(treffers) != 1:
        raise ValueError(f"INE-code {ine_code}: {len(treffers)} Wikidata-items gevonden in plaats van 1: {treffers}")
    return treffers[0]


def ophalen_coordinaten():
    """Bewaart per gemeente het kaartpunt (lon/lat) met de Wikidata-code als bron."""
    items = {ine: (kern or _item_voor_ine_code(ine)) for ine, _, _, kern in KAARTPUNTEN}
    ent = _wikidata({"action": "wbgetentities", "ids": "|".join(items.values()), "props": "claims"})["entities"]
    pad = RUW / "wikidata_coordinaten.csv"
    with pad.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ine_code", "gemeente", "kaartpunt", "wikidata", "lon", "lat", "opgehaald"])
        for ine, naam, kaartpunt, _ in KAARTPUNTEN:
            q = items[ine]
            coord = ent[q]["claims"]["P625"][0]["mainsnak"]["datavalue"]["value"]  # P625 = coördinaten
            w.writerow([ine, naam, kaartpunt, q, round(coord["longitude"], 4), round(coord["latitude"], 4),
                        date.today().isoformat()])
    print(f"Wikidata: {len(KAARTPUNTEN)} kaartpunten -> {pad}")


if __name__ == "__main__":
    ophalen_ine()
    ophalen_coordinaten()
