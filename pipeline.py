"""Pijplijn Woningprijzen Costa Blanca Zuid (opdracht stap 3).

Eén functie per stap, zonder Streamlit: elke functie krijgt data (of een pad)
binnen en geeft een DataFrame terug. app.py toont het resultaat van elke stap.
Rijnummers (rij ..) verwijzen naar beslissingslog.md.

Stap 1 OPHALEN    lees_idealista, lees_verkopen, lees_taxatie, lees_inwoners, lees_coordinaten
Stap 2 CONTROLEREN (volgt)
Stap 3 SAMENVOEGEN (volgt)
Stap 4 BEREKENEN  (volgt)
"""
import re
from pathlib import Path

import pandas as pd

RUW = Path(__file__).parent / "data" / "ruw"

# --------------------------------------------------------------------------
# Vaste gegevens
# --------------------------------------------------------------------------

# De 6 kustgemeentes, met de INE-code als sleutel (rij 80, punt 1)
GEMEENTEN = pd.DataFrame(
    [
        # ine_code, gemeente,              naam INE,               naam Ministerie
        ("03121", "Santa Pola",            "Santa Pola",           "Santa Pola"),
        ("03065", "Elche",                 "Elx/Elche",            "Elche/Elx"),
        ("03076", "Guardamar del Segura",  "Guardamar del Segura", "Guardamar del Segura"),
        ("03133", "Torrevieja",            "Torrevieja",           "Torrevieja"),
        ("03099", "Orihuela",              "Orihuela",             "Orihuela"),
        ("03902", "Pilar de la Horadada",  "Pilar de la Horadada", "Pilar de la Horadada"),
    ],
    columns=["ine_code", "gemeente", "naam_ine", "naam_ministerie"],
)

# Idealista-bestanden: bestandsnaam -> (ine_code van de gemeente, kustdistrict of None)
IDEALISTA_BESTANDEN = {
    "idealista_santa_pola.txt":        ("03121", None),
    "idealista_elche.txt":             ("03065", None),
    "idealista_guardamar.txt":         ("03076", None),
    "idealista_torrevieja.txt":        ("03133", None),
    "idealista_orihuela.txt":          ("03099", None),
    "idealista_pilar.txt":             ("03902", None),
    "idealista_elche_arenales.txt":    ("03065", "Arenales del Sol"),       # rij 65-67
    "idealista_elche_la_marina.txt":   ("03065", "La Marina"),
    "idealista_elche_el_altet.txt":    ("03065", "El Altet – Balsares"),
    "idealista_orihuela_costa.txt":    ("03099", "Orihuela Costa"),
}

# Maandnamen: Spaans (de meeste bestanden) en Nederlands (Torrevieja, vertaald door de browser)
_MAANDEN = {}
for _namen in ("enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre",
               "januari februari maart april mei juni juli augustus september oktober november december"):
    for _i, _m in enumerate(_namen.split(), start=1):
        _MAANDEN[_m] = _i

# Lege vakken: "n.d." (Spaans), "en" (Nederlandse vertaling van "n.d." bij Torrevieja)
_LEEG = {"n.d.", "en", "-", ""}


# --------------------------------------------------------------------------
# Stap 1 OPHALEN — elke bron omzetten naar een lange tabel (1 rij per gebied per periode)
# --------------------------------------------------------------------------

def _prijs(tekst):
    """'1.934 €/m2' of '€2.566/m2' of '€ 1.907/m2' -> 1934.0; leeg vak -> NaN."""
    tekst = str(tekst).strip()
    if tekst in _LEEG:
        return float("nan")
    gevonden = re.fullmatch(r"€?\s*(\d{1,3}(?:\.\d{3})*)\s*€?/m2", tekst)
    if not gevonden:
        raise ValueError(f"Onbekende prijsnotatie bij Idealista: {tekst!r}")
    return float(gevonden.group(1).replace(".", ""))


def lees_idealista(map_ruw=RUW):
    """Idealista-vraagprijzen: 10 bestanden x 250 maanden -> 1 rij per gebied per maand.

    Kolommen: bron_bestand, ine_code, kustdistrict (leeg = hele gemeente), jaar, maand, prijs_m2.
    """
    delen = []
    for bestand, (ine_code, district) in IDEALISTA_BESTANDEN.items():
        regels = (Path(map_ruw) / bestand).read_text(encoding="utf-8").splitlines()[1:]  # zonder kopregel
        rijen = []
        for regel in regels:
            if not regel.strip():
                continue
            kolommen = regel.split("\t")
            maandnaam, jaar = kolommen[0].strip().split()
            rijen.append((int(jaar), _MAANDEN[maandnaam.lower()], _prijs(kolommen[1])))
        deel = pd.DataFrame(rijen, columns=["jaar", "maand", "prijs_m2"])
        deel.insert(0, "kustdistrict", district)
        deel.insert(0, "ine_code", ine_code)
        deel.insert(0, "bron_bestand", bestand)
        delen.append(deel)
    return pd.concat(delen, ignore_index=True)


def lees_verkopen(pad=RUW / "ministerio_2.4_tweedehands_per_gemeente_34010250.xls"):
    """Ministerio tabel 2.4: aantal tweedehandsverkopen per gemeente per kwartaal (heel Spanje).

    In het Excelblad staan regio's, provincies en gemeentes onder elkaar in kolom B;
    regio- en provincierijen hebben geen cijfers. Kolommen: regio, provincie, naam_ministerie,
    jaar, kwartaal, aantal_verkopen, voorlopig.
    """
    blad = pd.read_excel(pad, header=None)
    jaren = blad.iloc[10].ffill()          # 'Año 2019' staat enkel boven het 1e kwartaal
    kwartalen = blad.iloc[12]               # '1º', '2º', ..., '2º (*)'
    datakolommen = [k for k in blad.columns if str(jaren[k]).startswith("Año")]

    data = blad.iloc[13:].copy()
    data["naam"] = data[1].astype(str).str.strip()
    data = data[(data["naam"] != "nan") & ~data["naam"].str.startswith("*")]   # lege rijen en voetnoot weg
    kopregel = data[datakolommen].isna().all(axis=1)                           # regio of provincie: geen cijfers
    regio_rij = kopregel & data["naam"].str.isupper()                          # regio's in HOOFDLETTERS
    data["regio"] = data["naam"].where(regio_rij).ffill()
    provincie = data["naam"].where(kopregel & ~regio_rij)
    data["provincie"] = provincie.groupby(data["regio"]).ffill()   # doorgeven binnen de regio, niet erover heen
    data = data[~kopregel]

    lang = data.melt(id_vars=["regio", "provincie", "naam"], value_vars=datakolommen,
                     var_name="kolom", value_name="aantal_verkopen")
    lang["jaar"] = lang["kolom"].map(lambda k: int(str(jaren[k]).split()[1]))
    lang["kwartaal"] = lang["kolom"].map(lambda k: int(str(kwartalen[k]).strip()[0]))
    lang["voorlopig"] = lang["kolom"].map(lambda k: "(*)" in str(kwartalen[k]))
    lang["aantal_verkopen"] = pd.to_numeric(lang["aantal_verkopen"])
    lang = lang.rename(columns={"naam": "naam_ministerie"})
    return lang[["regio", "provincie", "naam_ministerie", "jaar", "kwartaal", "aantal_verkopen", "voorlopig"]]


def lees_taxatie(pad=RUW / "ministerio_tabel4_valor_tasado_gemeentes_25000_35103500.xls"):
    """Ministerio tabel 4: taxatiewaarde per m2, 1 tabblad per kwartaal (gemeentes > 25.000 inwoners).

    Enkel tabbladen met de huidige opbouw (10 kolommen, splitsing naar ouderdom) worden gelezen;
    oudere bladen hebben een andere opbouw. Kolommen: blad, provincie, naam_ministerie, jaar,
    kwartaal, taxatie_tot5_m2, taxatie_meer5_m2, aantal_taxaties_meer5.
    """
    delen = []
    bladen = pd.read_excel(pad, sheet_name=None, header=None)   # alle tabbladen in één keer
    for naam, blad in bladen.items():
        gevonden = re.fullmatch(r"T([1-4])A(\d{4})", naam.strip())
        if not gevonden or blad.shape[1] != 10 or str(blad.iat[14, 2]).strip() != "Municipio":
            continue
        # controle op de lege kolom tussen prijzen en aantallen (fout van de AI op 05/11, B2 punt 5)
        if blad.iloc[17:, 6].notna().any():
            raise ValueError(f"Blad {naam}: kolom G is niet leeg - opbouw veranderd?")
        data = blad.iloc[17:, [1, 2, 3, 4, 8]].copy()
        data.columns = ["provincie", "naam_ministerie", "taxatie_tot5_m2", "taxatie_meer5_m2",
                        "aantal_taxaties_meer5"]
        data = data[data["naam_ministerie"].notna()]
        data["provincie"] = data["provincie"].ffill()   # provincie staat enkel op de 1e rij van het blok
        data.insert(0, "kwartaal", int(gevonden.group(1)))
        data.insert(0, "jaar", int(gevonden.group(2)))
        data.insert(0, "blad", naam.strip())
        delen.append(data)
    df = pd.concat(delen, ignore_index=True)
    for k in ["provincie", "naam_ministerie"]:
        df[k] = df[k].astype(str).str.strip()
    for k in ["taxatie_tot5_m2", "taxatie_meer5_m2", "aantal_taxaties_meer5"]:
        df[k] = pd.to_numeric(df[k], errors="coerce")   # 'n.r' (niet representatief) -> leeg
    return df


def lees_inwoners(pad=RUW / "ine_2856_inwoners.csv"):
    """INE tabel 2856: inwoners op 1 januari, alle gemeentes van Alicante, totaal/mannen/vrouwen.

    Reeksnaam 'Elx/Elche. Total. Total habitantes. Personas.' wordt gesplitst in naam en geslacht.
    """
    df = pd.read_csv(pad, dtype={"jaar": int})
    delen = df["reeks"].str.split(". ", n=2, regex=False)
    df.insert(1, "naam_ine", delen.str[0].str.strip())
    df.insert(2, "geslacht", delen.str[1].str.strip())
    return df.rename(columns={"waarde": "inwoners"})[["naam_ine", "geslacht", "jaar", "datum", "inwoners"]]


def lees_coordinaten(pad=RUW / "wikidata_coordinaten.csv"):
    """Wikidata: 1 kaartpunt per gemeente (rij 61-62, 75)."""
    return pd.read_csv(pad, dtype={"ine_code": str})
