"""Pijplijn Woningprijzen Costa Blanca Zuid (opdracht stap 3).

Eén functie per stap, zonder Streamlit: elke functie krijgt data (of een pad)
binnen en geeft een DataFrame terug. app.py toont het resultaat van elke stap.
Rijnummers (rij ..) verwijzen naar beslissingslog.md.

Stap 1 OPHALEN    lees_idealista, lees_verkopen, lees_taxatie, lees_inwoners, lees_coordinaten
Stap 2 CONTROLEREN stappen_idealista, stappen_verkopen, stappen_inwoners, stappen_taxatie, controle_taxatie
Stap 3 SAMENVOEGEN stappen_samenvoegen, kustdistricten_tabel, bewaar
Stap 4 BEREKENEN  jaar_op_jaar, stijging_periode, stap4_basistabel, stap4_districten, stijging_tabel

Alles in één keer uitvoeren en de CSV's wegschrijven (data/verwerkt):  python pipeline.py
"""
import re
from pathlib import Path

import pandas as pd

RUW = Path(__file__).parent / "data" / "ruw"
VERWERKT = Path(__file__).parent / "data" / "verwerkt"   # resultaat stap 3 (rij 88)

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
    """Wikidata: kaartpunten (rij 75, 92). Kolom district leeg = gemeente (centrum), ingevuld = kustdistrict."""
    return pd.read_csv(pad, dtype={"ine_code": str})


# --------------------------------------------------------------------------
# Stap 2 CONTROLEREN EN FILTEREN — per bron van ruwe rijen naar 1 rij per gemeente per jaar
# --------------------------------------------------------------------------
# Elke functie hieronder is een "pure functie": DataFrame erin, DataFrame eruit, niets anders.
# De functies stappen_* rijgen ze aan elkaar en onthouden na elke stap het resultaat + de reden,
# zodat de app de rijen-trechter kan tekenen (rij 76).

PERIODE = (2019, 2025)                                              # rij 11, 27
GEMEENTE_JAREN = len(GEMEENTEN) * (PERIODE[1] - PERIODE[0] + 1)     # 6 x 7 = 42


def filter_periode(df, van=PERIODE[0], tot=PERIODE[1]):
    """Houdt enkel de jaren van..tot (grenzen inbegrepen)."""
    return df[df["jaar"].between(van, tot)].reset_index(drop=True)


def splits_kustdistricten(df):
    """Idealista: (hele gemeentes, kustdistricten). Kustdistricten gaan apart verder (rij 65-67)."""
    is_district = df["kustdistrict"].notna()
    return df[~is_district].reset_index(drop=True), df[is_district].reset_index(drop=True)


def maand_naar_jaar(df, sleutels=("ine_code",)):
    """Vraagprijs per jaar = gemiddelde van de 12 maanden (rij 70).

    Ontbreekt er een maand, dan blijft het jaar leeg (niet opvullen, rij 40);
    de kolom aantal_maanden toont hoeveel maanden er meetelden.
    """
    groep = df.groupby([*sleutels, "jaar"], dropna=False)["prijs_m2"]
    uit = groep.agg(prijs_m2="mean", aantal_maanden="count").reset_index()
    uit.loc[uit["aantal_maanden"] < 12, "prijs_m2"] = float("nan")
    return uit


def maand_naar_kwartaal(df):
    """Vraagprijs per kwartaal = gemiddelde van de 3 maanden (rij 79); leeg als er een maand ontbreekt."""
    df = df.assign(kwartaal=(df["maand"] - 1) // 3 + 1)
    groep = df.groupby(["ine_code", "jaar", "kwartaal"])["prijs_m2"]
    uit = groep.agg(prijs_m2="mean", aantal_maanden="count").reset_index()
    uit.loc[uit["aantal_maanden"] < 3, "prijs_m2"] = float("nan")
    return uit


def filter_provincie_alicante(df):
    """Enkel gemeentes uit de provincie Alicante (rij 80, punt 2: geen Orihuela del Tremedal e.d.)."""
    return df[df["provincie"].isin(["Alicante/Alacant", "Alicante"])].reset_index(drop=True)


def filter_gemeenten(df, naamkolom):
    """Houdt enkel de 6 kustgemeentes en voegt de INE-code toe (rij 80, punt 1)."""
    uit = df.merge(GEMEENTEN[["ine_code", naamkolom]], on=naamkolom, how="inner")
    return uit[["ine_code", *df.columns]]


def kwartaal_naar_jaar(df, kolom, bewerking):
    """Kwartalen -> jaar met 'sum' (verkopen) of 'mean' (taxatie, rij 63); leeg als er een kwartaal ontbreekt."""
    groep = df.groupby(["ine_code", "jaar"])[kolom]
    uit = groep.agg(**{kolom: bewerking, "aantal_kwartalen": "count"}).reset_index()
    uit.loc[uit["aantal_kwartalen"] < 4, kolom] = float("nan")
    return uit


def filter_totaal(df):
    """INE: enkel het totaal aantal inwoners, niet mannen/vrouwen apart."""
    return df[df["geslacht"] == "Total"].reset_index(drop=True)


def ontbrekende_gemeente_jaren(df, waardekolom):
    """Gemeente-jaren (van de 42) zonder waarde: worden getoond, niet opgevuld (rij 40)."""
    alle = GEMEENTEN[["ine_code", "gemeente"]].merge(
        pd.DataFrame({"jaar": range(PERIODE[0], PERIODE[1] + 1)}), how="cross")
    samen = alle.merge(df[["ine_code", "jaar", waardekolom]], on=["ine_code", "jaar"], how="left")
    return samen[samen[waardekolom].isna()].reset_index(drop=True)


def _stap(stappen, naam, reden, df):
    """Onthoudt een tussenresultaat voor de trechter en geeft het onveranderd terug."""
    stappen.append({"stap": naam, "reden": reden, "rijen": len(df), "data": df})
    return df


def stappen_idealista(ruw):
    """Trechter Idealista: 2.500 maandrijen -> 42 gemeente-jaren (+ kustdistricten en kwartalen apart)."""
    s = []
    df = _stap(s, "ingelezen", "10 bestanden × 250 maanden", ruw)
    df, districten = splits_kustdistricten(df)
    _stap(s, "kustdistricten apart", f"{len(districten)} rijen van de 4 kustdistricten gaan apart verder (rij 65–67)", df)
    df = _stap(s, f"enkel {PERIODE[0]}–{PERIODE[1]}", "maanden buiten de periode weg", filter_periode(df))
    maanden = df
    df = _stap(s, "per jaar", "12 maanden → 1 jaargemiddelde (rij 70)", maand_naar_jaar(df))
    extra = {
        "kwartalen": maand_naar_kwartaal(maanden),                                       # rij 79, 82
        "districten": maand_naar_jaar(filter_periode(districten), ("ine_code", "kustdistrict")),
        "ontbrekend": ontbrekende_gemeente_jaren(df, "prijs_m2"),
    }
    return s, extra


def stappen_verkopen(ruw):
    """Trechter verkopen: alle gemeentes van Spanje per kwartaal -> 42 gemeente-jaren."""
    s = []
    df = _stap(s, "ingelezen", "alle gemeentes van Spanje × 90 kwartalen", ruw)
    df = _stap(s, "provincie Alicante", "andere provincies weg (rij 80)", filter_provincie_alicante(df))
    df = _stap(s, "6 kustgemeentes", "andere gemeentes van Alicante weg", filter_gemeenten(df, "naam_ministerie"))
    df = _stap(s, f"enkel {PERIODE[0]}–{PERIODE[1]}", "kwartalen buiten de periode weg", filter_periode(df))
    kwartalen = df
    df = _stap(s, "per jaar", "4 kwartalen → 1 jaarsom", kwartaal_naar_jaar(df, "aantal_verkopen", "sum"))
    return s, {"kwartalen": kwartalen, "ontbrekend": ontbrekende_gemeente_jaren(df, "aantal_verkopen")}


def stappen_inwoners(ruw):
    """Trechter inwoners: alle reeksen van INE-tabel 2856 -> 42 gemeente-jaren.

    Koppeling (rij 58, 75): 1/1/2026 bestaat nog niet -> verkopen van jaar X horen bij de telling van 1/1 van jaar X.
    """
    s = []
    df = _stap(s, "ingelezen", "alle gemeentes van Alicante × totaal/mannen/vrouwen × 8 jaar", ruw)
    df = _stap(s, "enkel totaal", "mannen en vrouwen apart weg", filter_totaal(df))
    df = _stap(s, "6 kustgemeentes", "andere gemeentes van Alicante weg", filter_gemeenten(df, "naam_ine"))
    df = _stap(s, f"enkel {PERIODE[0]}–{PERIODE[1]}", "telling van 1/1/2018 weg", filter_periode(df))
    return s, {"ontbrekend": ontbrekende_gemeente_jaren(df, "inwoners")}


def stappen_taxatie(ruw):
    """Taxatiewaarde (controle): alle gemeentes > 25.000 inwoners -> jaargemiddelde voor onze gemeentes."""
    s = []
    df = _stap(s, "ingelezen", "alle gemeentes > 25.000 inwoners × 66 kwartalen", ruw)
    df = _stap(s, "provincie Alicante", "andere provincies weg (rij 80)", filter_provincie_alicante(df))
    df = _stap(s, "kustgemeentes", "andere gemeentes weg; Guardamar en Pilar staan er niet in (< 25.000 inwoners)",
               filter_gemeenten(df, "naam_ministerie"))
    df = _stap(s, f"enkel {PERIODE[0]}–{PERIODE[1]}", "kwartalen buiten de periode weg", filter_periode(df))
    df = _stap(s, "per jaar", "4 kwartalen → 1 jaargemiddelde, kolom 'meer dan 5 jaar' (rij 63, 82)",
               kwartaal_naar_jaar(df, "taxatie_meer5_m2", "mean"))
    return s, {}


def controle_taxatie(prijs_jaar, taxatie_jaar):
    """Vraagprijs (Idealista) naast taxatiewaarde: verschil in % + tegengestelde richting (rij 77, 78).

    Tegengesteld = de ene stijgt en de andere daalt t.o.v. het jaar ervoor, hoe klein ook (rij 78).
    Blijft een van beide exact gelijk, dan telt dat niet als tegengesteld.
    """
    df = prijs_jaar[["ine_code", "jaar", "prijs_m2"]].merge(
        taxatie_jaar[["ine_code", "jaar", "taxatie_meer5_m2"]], on=["ine_code", "jaar"], how="inner")
    df = df.sort_values(["ine_code", "jaar"]).reset_index(drop=True)
    df["verschil_pct"] = (df["prijs_m2"] / df["taxatie_meer5_m2"] - 1) * 100
    groep = df.groupby("ine_code")
    df["prijs_verandering_pct"] = groep["prijs_m2"].pct_change() * 100
    df["taxatie_verandering_pct"] = groep["taxatie_meer5_m2"].pct_change() * 100
    df["tegengesteld"] = (df["prijs_verandering_pct"] * df["taxatie_verandering_pct"]) < 0
    return GEMEENTEN[["ine_code", "gemeente"]].merge(df, on="ine_code")


# --------------------------------------------------------------------------
# Stap 3 SAMENVOEGEN — één basistabel gemeente × jaar (42 rijen) + kustdistricten apart
# --------------------------------------------------------------------------

def raster():
    """Alle 42 combinaties gemeente × jaar: het vaste vertrekpunt van stap 3 (rij 86)."""
    jaren = pd.DataFrame({"jaar": range(PERIODE[0], PERIODE[1] + 1)})
    return GEMEENTEN[["ine_code", "gemeente"]].merge(jaren, how="cross")


def koppel(basis, bron, kolommen, sleutels=("ine_code", "jaar")):
    """Left join (rij 86): alle rijen van basis blijven; geen cijfer in de bron -> leeg vak.

    validate='many_to_one' stopt de pijplijn als een bron dubbele sleutels heeft
    (dan zou het aantal rijen stil stijgen boven 42).
    """
    return basis.merge(bron[[*sleutels, *kolommen]], on=list(sleutels), how="left", validate="many_to_one")


def stappen_samenvoegen(prijs_jaar, verkopen_jaar, inwoners_jaar, taxatie_jaar, controle, coordinaten):
    """Trechter samenvoegen: raster van 42 rijen + elke bron eraan (left join) -> basistabel.

    Kolommen: ine_code | gemeente | jaar | prijs_m2 | aantal_verkopen | inwoners | verkopen_per_1000 |
    taxatiewaarde_m2 | lat | lon | taxatie_tegenstrijdig  (spec stap 3, rij 85, 92).
    """
    s = []
    taxatie = taxatie_jaar.rename(columns={"taxatie_meer5_m2": "taxatiewaarde_m2"})
    # Tegenstrijdig enkel waar vergelijken kan; geen vorig jaar (2019) -> leeg vak (<NA>), niet False (rij 89)
    niet_te_vergelijken = controle[["prijs_verandering_pct", "taxatie_verandering_pct"]].isna().any(axis=1)
    controle = controle.assign(
        taxatie_tegenstrijdig=controle["tegengesteld"].astype("boolean").mask(niet_te_vergelijken))
    coord = coordinaten[coordinaten["district"].isna()]     # enkel de gemeentes, districten apart (rij 92)

    df = _stap(s, "raster", "6 gemeentes × 7 jaar (rij 86)", raster())
    df = _stap(s, "+ vraagprijs", "Idealista, jaargemiddelde (rij 70)", koppel(df, prijs_jaar, ["prijs_m2"]))
    df = _stap(s, "+ verkopen", "Ministerio, jaarsom", koppel(df, verkopen_jaar, ["aantal_verkopen"]))
    df = _stap(s, "+ inwoners", "INE, telling 1/1 van hetzelfde jaar (rij 58)", koppel(df, inwoners_jaar, ["inwoners"]))
    df = _stap(s, "+ taxatie", "Ministerio, enkel 4 gemeentes; Guardamar en Pilar leeg (rij 80)",
               koppel(df, taxatie, ["taxatiewaarde_m2"]))
    df = _stap(s, "+ controle taxatie", "markering tegengestelde richting (rij 78, 85)",
               koppel(df, controle, ["taxatie_tegenstrijdig"]))
    df = _stap(s, "+ coördinaten", "Wikidata, centrum van elke gemeente (rij 92)",
               koppel(df, coord, ["lat", "lon"], sleutels=("ine_code",)))

    df["aantal_verkopen"] = df["aantal_verkopen"].astype("Int64")      # gehele getallen, leeg blijft mogelijk
    df["inwoners"] = df["inwoners"].astype("Int64")
    df["verkopen_per_1000"] = df["aantal_verkopen"] / df["inwoners"] * 1000
    # Guardamar en Pilar (geen taxatie) komen niet voor in de controle -> na de left join ook leeg (rij 89)
    df["taxatie_tegenstrijdig"] = df["taxatie_tegenstrijdig"].astype("boolean")
    volgorde = ["ine_code", "gemeente", "jaar", "prijs_m2", "aantal_verkopen", "inwoners", "verkopen_per_1000",
                "taxatiewaarde_m2", "lat", "lon", "taxatie_tegenstrijdig"]
    df = df[volgorde]
    if len(df) != GEMEENTE_JAREN:
        raise ValueError(f"Basistabel heeft {len(df)} rijen in plaats van {GEMEENTE_JAREN}")
    return s, {"basistabel": df}


def kustdistricten_tabel(districten_jaar, coordinaten):
    """Kustdistricten apart, enkel vraagprijs (rij 87) + eigen kaartpunt (rij 91-92):
    district | gemeente | jaar | prijs_m2 | lat | lon (28 rijen)."""
    df = districten_jaar.merge(GEMEENTEN[["ine_code", "gemeente"]], on="ine_code", how="left")
    df = df.rename(columns={"kustdistrict": "district"})
    df = koppel(df, coordinaten[coordinaten["district"].notna()], ["lat", "lon"], sleutels=("district",))
    cols = ["district", "gemeente", "jaar", "prijs_m2", "lat", "lon"]
    return df[cols].sort_values(["gemeente", "district", "jaar"]).reset_index(drop=True)


def bewaar(tabellen, map_uit=VERWERKT):
    """Schrijft de resultaten weg (rij 88, 97): tabellen = {"basistabel": df, ...} -> <naam>.csv.

    Formaat voor een Belgische Excel: puntkomma als scheidingsteken, komma als decimaalteken,
    utf-8 met BOM (zodat Excel de tekens juist toont). Terug inlezen: lees_verwerkt().
    """
    map_uit = Path(map_uit)
    map_uit.mkdir(parents=True, exist_ok=True)
    opties = {"sep": ";", "decimal": ",", "index": False, "encoding": "utf-8-sig"}
    # bedragen en verhoudingen op 2 decimalen; coördinaten (lat, lon) blijven volledig (4 decimalen)
    paden = []
    for naam, df in tabellen.items():
        # bedragen, verhoudingen en percentages op 2 decimalen; coördinaten (lat, lon) blijven volledig
        afronden = {k: 2 for k in df.columns if k.startswith(("prijs", "verkopen_per_1000", "taxatie"))
                    or k.endswith("_pct")}
        pad = map_uit / f"{naam}.csv"
        df.round(afronden).to_csv(pad, **opties)
        paden.append(pad)
    return paden


def lees_verwerkt(naam, map_in=VERWERKT):
    """Leest een CSV uit data/verwerkt terug in (zelfde formaat als bewaar)."""
    return pd.read_csv(Path(map_in) / naam, sep=";", decimal=",", encoding="utf-8-sig", dtype={"ine_code": str})


def voer_uit():
    """Volledige pijplijn stap 1-3 zonder app; geeft alle tussenresultaten terug."""
    stap2 = {
        "idealista": stappen_idealista(lees_idealista()),
        "verkopen": stappen_verkopen(lees_verkopen()),
        "inwoners": stappen_inwoners(lees_inwoners()),
        "taxatie": stappen_taxatie(lees_taxatie()),
    }
    eind = {naam: stappen[-1]["data"] for naam, (stappen, _) in stap2.items()}
    controle = controle_taxatie(eind["idealista"], eind["taxatie"])
    coordinaten = lees_coordinaten()
    stap3 = stappen_samenvoegen(eind["idealista"], eind["verkopen"], eind["inwoners"], eind["taxatie"],
                                controle, coordinaten)
    districten = kustdistricten_tabel(stap2["idealista"][1]["districten"], coordinaten)
    basistabel4 = stap4_basistabel(stap3[1]["basistabel"])
    districten4 = stap4_districten(districten)
    stijging = stijging_tabel(basistabel4, districten4)
    kwartalen = kwartaal_tabel(stap2["idealista"][1]["kwartalen"], stap2["verkopen"][1]["kwartalen"])  # rij 100
    return stap2, controle, stap3, {"basistabel": basistabel4, "kustdistricten": districten4, "stijging": stijging,
                                    "kwartalen": kwartalen}


# --------------------------------------------------------------------------
# Stap 4 BEREKENEN — stijging jaar op jaar (rij 96) en 2019 -> 2025 (rij 22, 94-97)
# --------------------------------------------------------------------------
# Ontbreekt een waarde, dan blijft de stijging leeg: niets opvullen (rij 40).

def jaar_op_jaar(df, kolom, groep):
    """% verandering t.o.v. het jaar ervoor, per gebied; het eerste jaar (2019) blijft leeg (rij 96).

    Voorbeeld: 1.452 (2019) -> 1.483 (2020) geeft (1.483 / 1.452 - 1) x 100 = +2,1 %.
    """
    df = df.sort_values([groep, "jaar"])
    vorige = df.groupby(groep)[kolom].shift(1)            # waarde van het jaar ervoor, binnen hetzelfde gebied
    vorig_jaar = df.groupby(groep)["jaar"].shift(1)
    pct = (df[kolom] / vorige - 1) * 100
    return pct.where(vorig_jaar == df["jaar"] - 1)        # enkel als het vorige jaar echt het jaar ervoor is


def stijging_periode(df, kolom, groep, van=PERIODE[0], tot=PERIODE[1]):
    """% stijging van het jaar van tot het jaar tot, per gebied: (waarde tot / waarde van - 1) x 100.

    Geeft een tabel: groep | <kolom>_<van> | <kolom>_<tot> | <kolom>_stijging_pct.
    """
    breed = df[df["jaar"].isin([van, tot])].pivot(index=groep, columns="jaar", values=kolom)
    uit = pd.DataFrame({
        f"{kolom}_{van}": breed.get(van),
        f"{kolom}_{tot}": breed.get(tot),
    })
    uit[f"{kolom}_stijging_pct"] = (uit[f"{kolom}_{tot}"] / uit[f"{kolom}_{van}"] - 1) * 100
    return uit.reset_index()


def stap4_basistabel(basistabel):
    """Basistabel + 3 kolommen jaar op jaar (rij 94, 96, 97): prijs, verkopen absoluut en per 1.000 inwoners."""
    df = basistabel.sort_values(["ine_code", "jaar"]).copy()
    for kolom in ["prijs_m2", "aantal_verkopen", "verkopen_per_1000"]:
        df[f"{kolom}_jaar_pct"] = jaar_op_jaar(df.astype({kolom: "float"}), kolom, "ine_code")
    # zelfde volgorde van de gemeentes als in stap 3
    return df.set_index(["ine_code", "jaar"]).loc[basistabel.set_index(["ine_code", "jaar"]).index].reset_index()[
        [*basistabel.columns, "prijs_m2_jaar_pct", "aantal_verkopen_jaar_pct", "verkopen_per_1000_jaar_pct"]]


def stap4_districten(districten):
    """Kustdistricten + prijs jaar op jaar (rij 95, 96)."""
    df = districten.copy()
    df["prijs_m2_jaar_pct"] = jaar_op_jaar(df, "prijs_m2", "district")
    return df.sort_values(["gemeente", "district", "jaar"]).reset_index(drop=True)


def stijging_tabel(basistabel, districten):
    """Stijging 2019 -> 2025: 1 rij per gemeente (6) en per kustdistrict (4) = 10 rijen (rij 95, 97).

    Gemeentes: prijs, aantal verkopen en verkopen per 1.000 inwoners (rij 94). Districten: enkel prijs.
    Kolommen: soort | gemeente | district | <maatstaf>_2019 | <maatstaf>_2025 | <maatstaf>_stijging_pct.
    """
    delen = [stijging_periode(basistabel, k, "gemeente") for k in ["prijs_m2", "aantal_verkopen", "verkopen_per_1000"]]
    gemeentes = delen[0].merge(delen[1], on="gemeente", validate="one_to_one").merge(delen[2], on="gemeente",
                                                                                     validate="one_to_one")
    gemeentes.insert(0, "soort", "gemeente")
    gemeentes.insert(2, "district", pd.NA)
    gemeentes = GEMEENTEN[["gemeente"]].merge(gemeentes, on="gemeente")    # vaste volgorde van de gemeentes

    dist = stijging_periode(districten, "prijs_m2", "district")
    dist = dist.merge(districten[["district", "gemeente"]].drop_duplicates(), on="district", validate="one_to_one")
    dist.insert(0, "soort", "kustdistrict")
    uit = pd.concat([gemeentes, dist], ignore_index=True)
    return uit[["soort", "gemeente", "district", *[k for k in gemeentes.columns if k not in ("soort", "gemeente", "district")]]]


def kwartaal_tabel(prijs_kwartalen, verkopen_kwartalen):
    """Kwartaaltabel voor de coronagrafiek E5 (rij 79, 82, 100): 6 gemeentes × 28 kwartalen = 168 rijen.

    Zelfde werkwijze als de basistabel (rij 86): eerst een vast raster, dan elke bron met een left join,
    zodat er geen kwartaal stil verdwijnt; ontbreekt een cijfer, dan blijft het vak leeg (rij 40).
    Kolommen: ine_code | gemeente | jaar | kwartaal | periode (bv. '2020 K2') | prijs_m2 | aantal_verkopen.
    """
    sleutels = ["ine_code", "jaar", "kwartaal"]
    kwartalen = pd.DataFrame([(j, k) for j in range(PERIODE[0], PERIODE[1] + 1) for k in range(1, 5)],
                             columns=["jaar", "kwartaal"])
    df = GEMEENTEN[["ine_code", "gemeente"]].merge(kwartalen, how="cross")
    df = df.merge(prijs_kwartalen[[*sleutels, "prijs_m2"]], on=sleutels, how="left", validate="one_to_one")
    df = df.merge(verkopen_kwartalen[[*sleutels, "aantal_verkopen"]], on=sleutels, how="left",
                  validate="one_to_one")
    df.insert(4, "periode", df["jaar"].astype(str) + " K" + df["kwartaal"].astype(str))
    return df


if __name__ == "__main__":
    _, _, _, tabellen = voer_uit()
    for pad in bewaar(tabellen):
        print("geschreven:", pad)
    with pd.option_context("display.width", 250, "display.max_columns", 20):
        print(tabellen["stijging"].round(1).to_string())
