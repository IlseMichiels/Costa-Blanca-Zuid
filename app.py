"""Streamlit-app Woningprijzen Costa Blanca Zuid.

Starten:  conda activate syntra-ds   en dan   streamlit run app.py
Alle rekenwerk zit in pipeline.py; deze app toont enkel wat elke stap doet.
"""
import streamlit as st

import pipeline as pl

st.set_page_config(page_title="Woningprijzen Costa Blanca Zuid", layout="wide")


def getal(n):
    """Belgische notatie: 1234567 -> '1.234.567' (rij 80, punt 7)."""
    return f"{n:,.0f}".replace(",", ".")


# Inlezen met caching: de bestanden worden maar één keer gelezen (het verkopenbestand duurt ± 30 s)
@st.cache_data(show_spinner="Idealista inlezen...")
def idealista():
    return pl.lees_idealista()


@st.cache_data(show_spinner="Verkopen (Ministerio) inlezen... dit duurt ± 30 seconden")
def verkopen():
    return pl.lees_verkopen()


@st.cache_data(show_spinner="Taxatiewaarden (Ministerio) inlezen...")
def taxatie():
    return pl.lees_taxatie()


@st.cache_data(show_spinner="Inwoners (INE) inlezen...")
def inwoners():
    return pl.lees_inwoners()


@st.cache_data(show_spinner="Coördinaten inlezen...")
def coordinaten():
    return pl.lees_coordinaten()


# --------------------------------------------------------------------------
st.title("Woningprijzen Costa Blanca Zuid")
st.markdown(
    "**Hoofdvraag:** hoe verhouden de zes kustgemeentes van de Costa Blanca Zuid zich tot elkaar "
    "qua vraagprijs per m², aantal verkochte tweedehandswoningen en prijsevolutie tussen 2019 en 2025? "
    "*(mission_statement_v2.md)*"
)
st.info("Pijplijn in opbouw — stap 1 (ophalen) is klaar; stap 2–4 en de rijen-trechters volgen.")

# --------------------------------------------------------------------------
st.header("Stap 1 · Ophalen")
st.caption("Elke bron wordt ingelezen zoals ze is en omgezet naar een lange tabel: één rij per gebied per periode. "
           "Er valt hier nog niets weg — filteren gebeurt in stap 2.")

df_i, df_v, df_t, df_w, df_c = idealista(), verkopen(), taxatie(), inwoners(), coordinaten()

with st.expander(f"Idealista — vraagprijs per m² per maand · {getal(len(df_i))} rijen"):
    st.markdown(
        "- **Bron:** 10 tekstbestanden in `data/ruw/` (gekopieerd van idealista.com, rij 64): "
        "6 gemeentes + 4 kustdistricten (rij 65–67)\n"
        f"- **Rijen:** 10 bestanden × 250 maanden (01/2006–10/2026) = {getal(len(df_i))}\n"
        f"- **Lege prijzen** (n.d., vooral de eerste jaren): {getal(df_i['prijs_m2'].isna().sum())}"
    )
    st.dataframe(df_i.groupby("bron_bestand", sort=False).size().rename("rijen"), width="content")
    st.markdown("**Voorbeeld:**")
    st.dataframe(df_i.head(10), hide_index=True)

with st.expander(f"Ministerio tabel 2.4 — tweedehandsverkopen per kwartaal · {getal(len(df_v))} rijen"):
    st.markdown(
        "- **Bron:** `ministerio_2.4_tweedehands_per_gemeente_34010250.xls` (alle gemeentes van Spanje)\n"
        f"- **Rijen:** {getal(df_v['naam_ministerie'].nunique())} gemeentenamen × "
        f"{df_v.groupby(['jaar', 'kwartaal']).ngroups} kwartalen ({df_v['jaar'].min()}–{df_v['jaar'].max()}) "
        f"= {getal(len(df_v))}\n"
        f"- **Lege aantallen** (elders in Spanje): {getal(df_v['aantal_verkopen'].isna().sum())} · "
        f"**voorlopige cijfers** (laatste kwartaal): {getal(df_v['voorlopig'].sum())}"
    )
    st.markdown("**Voorbeeld — Torrevieja 2020:**")
    st.dataframe(df_v[(df_v["naam_ministerie"] == "Torrevieja") & (df_v["jaar"] == 2020)], hide_index=True)

with st.expander(f"Ministerio tabel 4 — taxatiewaarde per m² per kwartaal (controle) · {getal(len(df_t))} rijen"):
    st.markdown(
        "- **Bron:** `ministerio_tabel4_valor_tasado_gemeentes_25000_35103500.xls`, 1 tabblad per kwartaal, "
        "enkel gemeentes met meer dan 25.000 inwoners\n"
        f"- **Gelezen tabbladen:** {df_t['blad'].nunique()} ({df_t['jaar'].min()}–{df_t['jaar'].max()}); "
        "oudere bladen hebben een andere opbouw (geen splitsing naar ouderdom) en worden overgeslagen\n"
        "- We gebruiken de kolom **meer dan 5 jaar** = tweedehands (rij 56, 82); 'n.r' (niet representatief) wordt leeg"
    )
    st.markdown("**Voorbeeld — Torrevieja 2025:**")
    st.dataframe(df_t[(df_t["naam_ministerie"] == "Torrevieja") & (df_t["jaar"] == 2025)], hide_index=True)

with st.expander(f"INE tabel 2856 — inwoners op 1 januari · {getal(len(df_w))} rijen"):
    st.markdown(
        "- **Bron:** `ine_2856_inwoners.csv` (opgehaald met `ophalen_bronnen.py`, rij 75): "
        "alle gemeentes van Alicante, totaal / mannen / vrouwen\n"
        f"- **Jaren:** {df_w['jaar'].min()}–{df_w['jaar'].max()} (laatste telling: 1/1/{df_w['jaar'].max()})"
    )
    st.markdown("**Voorbeeld:**")
    st.dataframe(df_w.head(6), hide_index=True)

with st.expander(f"Wikidata — kaartpunten · {getal(len(df_c))} rijen"):
    st.markdown("- **Bron:** `wikidata_coordinaten.csv`; Elche en Orihuela = kustkern (rij 61–62)")
    st.dataframe(df_c, hide_index=True)
