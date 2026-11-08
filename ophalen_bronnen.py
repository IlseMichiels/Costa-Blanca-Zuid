"""Haalt de bronnen op die via internet beschikbaar zijn en bewaart ze in data/ruw/.

Los van pipeline.py: dit script gebruikt internet, de pipeline niet (rij 75).
Opnieuw ophalen (bv. als INE de telling van 1/1/2026 publiceert):

    conda activate syntra-ds
    python ophalen_bronnen.py              (alles)
    python ophalen_bronnen.py inwoners     (enkel INE)
    python ophalen_bronnen.py coordinaten  (enkel kaartpunten)

Bronnen:
- INE tabel 2856 "Alicante/Alacant: Población por municipios y sexo" (B4, rij 54)
- Wikidata + OpenStreetMap: coördinaten van de kaartpunten (B7, rij 61-62, herzien in rij 91-92)
"""
import csv
import json
import sys
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

RUW = Path(__file__).parent / "data" / "ruw"
USER_AGENT = "SyntraCursusProject/1.0 (studieproject Costa Blanca Zuid)"

INE_URL = "https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/2856?nult=8&tip=A"

# Kaartpunten gemeentes (rij 92): centrum van de hoofdkern, voor alle 6 gemeentes.
# Gezocht via de INE-code (Wikidata-eigenschap P772).
GEMEENTE_PUNTEN = [
    # (ine_code, gemeente)
    ("03065", "Elche"),
    ("03133", "Torrevieja"),
    ("03121", "Santa Pola"),
    ("03099", "Orihuela"),
    ("03076", "Guardamar del Segura"),
    ("03902", "Pilar de la Horadada"),
]

# Kaartpunten kustdistricten (rij 91-92): woonkern, geen strand (rij 62).
# De districtnaam is dezelfde als in pipeline.IDEALISTA_BESTANDEN (sleutel voor de koppeling).
DISTRICT_PUNTEN = [
    # (ine_code, gemeente, district, kaartpunt, bron, bron_id)
    ("03065", "Elche", "Arenales del Sol", "woonkern Los Arenales del Sol", "wikidata", "Q9023882"),
    ("03065", "Elche", "La Marina", "woonkern la Marina", "openstreetmap", "N390185380"),   # niet in Wikidata
    ("03065", "Elche", "El Altet – Balsares", "woonkern El Altet (Balsares heeft geen eigen kaartpunt)",
     "wikidata", "Q6746200"),
    ("03099", "Orihuela", "Orihuela Costa", "woonkern Orihuela Costa", "wikidata", "Q2803214"),
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
NOMINATIM_LOOKUP = "https://nominatim.openstreetmap.org/lookup?"


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


def _osm_punt(osm_id):
    """OpenStreetMap (Nominatim lookup) via vast object-nummer, bv. 'N390185380' -> (lon, lat)."""
    res = _get_json(NOMINATIM_LOOKUP + urllib.parse.urlencode({"osm_ids": osm_id, "format": "jsonv2"}))
    if len(res) != 1:
        raise ValueError(f"OpenStreetMap {osm_id}: {len(res)} resultaten in plaats van 1")
    return float(res[0]["lon"]), float(res[0]["lat"])


def ophalen_coordinaten():
    """Bewaart de kaartpunten (lon/lat): 6 gemeentes (centrum) + 4 kustdistricten, met de bron per punt.

    Kolom district leeg = gemeente; ingevuld = kustdistrict.
    """
    gemeente_items = {ine: _item_voor_ine_code(ine) for ine, _ in GEMEENTE_PUNTEN}
    wd_ids = list(gemeente_items.values()) + [b_id for *_, bron, b_id in DISTRICT_PUNTEN if bron == "wikidata"]
    ent = _wikidata({"action": "wbgetentities", "ids": "|".join(wd_ids), "props": "claims"})["entities"]

    def wd_punt(q):
        coord = ent[q]["claims"]["P625"][0]["mainsnak"]["datavalue"]["value"]   # P625 = coördinaten
        return coord["longitude"], coord["latitude"]

    rijen = [(ine, naam, "", "centrum", "wikidata", gemeente_items[ine], *wd_punt(gemeente_items[ine]))
             for ine, naam in GEMEENTE_PUNTEN]
    for ine, naam, district, kaartpunt, bron, b_id in DISTRICT_PUNTEN:
        lon, lat = wd_punt(b_id) if bron == "wikidata" else _osm_punt(b_id)
        rijen.append((ine, naam, district, kaartpunt, bron, b_id, lon, lat))

    pad = RUW / "wikidata_coordinaten.csv"
    with pad.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ine_code", "gemeente", "district", "kaartpunt", "bron", "bron_id", "lon", "lat", "opgehaald"])
        for ine, naam, district, kaartpunt, bron, b_id, lon, lat in rijen:
            w.writerow([ine, naam, district, kaartpunt, bron, b_id, round(lon, 4), round(lat, 4), date.today().isoformat()])
    print(f"Coördinaten: {len(GEMEENTE_PUNTEN)} gemeentes + {len(DISTRICT_PUNTEN)} kustdistricten -> {pad}")


if __name__ == "__main__":
    keuze = sys.argv[1] if len(sys.argv) > 1 else "alles"
    if keuze in ("alles", "inwoners"):
        ophalen_ine()
    if keuze in ("alles", "coordinaten"):
        ophalen_coordinaten()
