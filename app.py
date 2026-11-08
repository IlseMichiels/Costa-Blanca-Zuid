"""Streamlit-app Woningprijzen Costa Blanca Zuid.

Starten:  conda activate syntra-ds   en dan   streamlit run app.py
Alle rekenwerk zit in pipeline.py; deze app toont enkel wat elke stap doet.
"""
import altair as alt
import pandas as pd
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


@st.cache_data(show_spinner="Stap 2 uitvoeren...")
def stap2():
    return {
        "Idealista (vraagprijs)": pl.stappen_idealista(idealista()),
        "Ministerio (verkopen)": pl.stappen_verkopen(verkopen()),
        "INE (inwoners)": pl.stappen_inwoners(inwoners()),
        "Ministerio (taxatie, controle)": pl.stappen_taxatie(taxatie()),
    }


@st.cache_data(show_spinner="Stap 3 uitvoeren...")
def stap3():
    r = stap2()
    eind = {naam: stappen[-1]["data"] for naam, (stappen, _) in r.items()}
    controle = pl.controle_taxatie(eind["Idealista (vraagprijs)"], eind["Ministerio (taxatie, controle)"])
    stappen, extra = pl.stappen_samenvoegen(
        eind["Idealista (vraagprijs)"], eind["Ministerio (verkopen)"], eind["INE (inwoners)"],
        eind["Ministerio (taxatie, controle)"], controle, coordinaten())
    return stappen, extra["basistabel"], pl.kustdistricten_tabel(r["Idealista (vraagprijs)"][1]["districten"],
                                                                  coordinaten())


@st.cache_data(show_spinner="Stap 4 uitvoeren...")
def stap4():
    _, basistabel, districten = stap3()
    basistabel4 = pl.stap4_basistabel(basistabel)
    districten4 = pl.stap4_districten(districten)
    return basistabel4, districten4, pl.stijging_tabel(basistabel4, districten4)


def trechter(stappen, titel):
    """Horizontale balken: aantal rijen na elke stap (logaritmische as: van 732.600 tot 42 past op één figuur)."""
    df = pd.DataFrame([{"stap": f"{i + 1}. {s['stap']}", "rijen": s["rijen"], "label": getal(s["rijen"])}
                       for i, s in enumerate(stappen)])
    basis = alt.Chart(df, title=titel).encode(
        y=alt.Y("stap:N", sort=None, title=None),
        x=alt.X("rijen:Q", scale=alt.Scale(type="log"), title="rijen (log-schaal)"),
        tooltip=["stap", "label"],
    )
    return (basis.mark_bar(color="#2a7f9e") + basis.mark_text(align="left", dx=4).encode(text="label")).properties(height=170)


def stappentabel(stappen):
    """Tabel per stap: rijen erin, eruit, verschil en de reden (opdracht stap 3)."""
    rijen = []
    for i, s in enumerate(stappen):
        voor = stappen[i - 1]["rijen"] if i else None
        rijen.append({"stap": s["stap"], "rijen in": getal(voor) if voor is not None else "—",
                      "rijen uit": getal(s["rijen"]),
                      "verschil": getal(s["rijen"] - voor) if voor is not None else "—", "waarom": s["reden"]})
    return pd.DataFrame(rijen)


# --------------------------------------------------------------------------
st.title("Woningprijzen Costa Blanca Zuid")
st.markdown(
    "**Hoofdvraag:** hoe verhouden de zes kustgemeentes van de Costa Blanca Zuid zich tot elkaar "
    "qua vraagprijs per m², aantal verkochte tweedehandswoningen en prijsevolutie tussen 2019 en 2025? "
    "*(mission_statement_v2.md)*"
)
st.info("Pijplijn klaar — stap 1 (ophalen), stap 2 (controleren en filteren), stap 3 (samenvoegen) en "
        "stap 4 (berekenen). Het dashboard (grafieken, kaart, conclusies) volgt.")

# --------------------------------------------------------------------------
st.header("Rijen-trechters")
st.caption("Per bron: hoeveel rijen er na elke stap overblijven (rij 76). Elke bron eindigt op "
           f"{pl.GEMEENTE_JAREN} rijen = 6 gemeentes × 7 jaar. De vierde trechter (samenvoegen) moet constant op "
           f"{pl.GEMEENTE_JAREN} blijven: daalt of stijgt hij, dan ging er bij het koppelen iets mis (rij 86). "
           "Waarom rijen wegvallen: zie de uitklapblokken onder Stap 2 en 3.")
resultaten = stap2()
stappen3, basistabel, districten = stap3()
kolommen = st.columns(4)
for kolom, naam in zip(kolommen, ["Idealista (vraagprijs)", "Ministerio (verkopen)", "INE (inwoners)"]):
    with kolom:
        st.altair_chart(trechter(resultaten[naam][0], naam), width="stretch")
with kolommen[3]:
    st.altair_chart(trechter(stappen3, "Samenvoegen (basistabel)"), width="stretch")

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
    st.markdown("- **Bron:** `wikidata_coordinaten.csv`: het centrum van elke gemeente + een eigen kaartpunt "
                "voor de 4 kustdistricten (rij 91–92; herziening van rij 61)")
    st.dataframe(df_c, hide_index=True)

# --------------------------------------------------------------------------
st.header("Stap 2 · Controleren en filteren")
st.caption("Per bron van ruwe rijen naar één rij per gemeente per jaar. Ontbrekende waarden worden "
           "opgelijst, nooit opgevuld (rij 40).")

for naam in ["Idealista (vraagprijs)", "Ministerio (verkopen)", "INE (inwoners)"]:
    stappen, extra = resultaten[naam]
    eind = stappen[-1]["data"]
    with st.expander(f"{naam} · {getal(stappen[0]['rijen'])} → {getal(stappen[-1]['rijen'])} rijen"):
        st.dataframe(stappentabel(stappen), hide_index=True)
        ontbrekend = extra["ontbrekend"]
        if len(ontbrekend):
            st.warning(f"{len(ontbrekend)} gemeente-jaren zonder waarde (niet opgevuld):")
            st.dataframe(ontbrekend, hide_index=True)
        else:
            st.success(f"Geen ontbrekende gemeente-jaren: alle {pl.GEMEENTE_JAREN} aanwezig.")
        st.markdown("**Resultaat na de laatste stap** (met gemeentenaam):")
        st.dataframe(pl.GEMEENTEN[["ine_code", "gemeente"]].merge(eind, on="ine_code"), hide_index=True)
        if "districten" in extra:
            st.markdown("**Kustdistricten apart** (enkel vraagprijs, rij 65–67): "
                        f"{len(extra['districten'])} rijen = 4 districten × 7 jaar")
            st.dataframe(extra["districten"], hide_index=True)
        if "kwartalen" in extra:
            st.markdown(f"**Per kwartaal** voor de coronagrafiek (rij 79, 82): {len(extra['kwartalen'])} rijen "
                        "= 6 gemeentes × 28 kwartalen")
            st.dataframe(extra["kwartalen"], hide_index=True)

stappen_t, _ = resultaten["Ministerio (taxatie, controle)"]
controle = pl.controle_taxatie(resultaten["Idealista (vraagprijs)"][0][-1]["data"], stappen_t[-1]["data"])
n_tegen = int(controle["tegengesteld"].sum())
n_vergelijk = int(controle["prijs_verandering_pct"].notna().sum())
with st.expander(f"Controle: vraagprijs ↔ taxatiewaarde · {n_tegen} tegenstrijdigheden op {n_vergelijk} vergelijkingen"):
    st.markdown(
        "- **Waarom:** de taxatiewaarde van het Ministerie dient als controle voor de vraagprijs van Idealista "
        "(rij 48, 63). Een vraagprijs ligt normaal hoger dan een taxatie, dus een verschil op zich is geen fout.\n"
        "- **Wat je ziet:** het verschil in % en, per jaar, of beide in **tegengestelde richting** bewegen "
        "(de ene stijgt, de andere daalt), hoe klein ook (rij 77, 78).\n"
        "- **Enkel 4 van de 6 gemeentes:** Guardamar del Segura en Pilar de la Horadada hebben minder dan "
        "25.000 inwoners en dus geen taxatiewaarde → geen controlecijfer."
    )
    st.dataframe(stappentabel(stappen_t), hide_index=True)
    tabel = controle.copy()
    tabel["tegengesteld"] = tabel["tegengesteld"].map({True: "⚠️ ja", False: ""})
    st.dataframe(
        tabel.drop(columns="ine_code"), hide_index=True,
        column_config={
            "prijs_m2": st.column_config.NumberColumn("vraagprijs €/m²", format="%.0f"),
            "taxatie_meer5_m2": st.column_config.NumberColumn("taxatie €/m²", format="%.0f"),
            "verschil_pct": st.column_config.NumberColumn("verschil %", format="%.1f"),
            "prijs_verandering_pct": st.column_config.NumberColumn("vraagprijs t.o.v. vorig jaar %", format="%.1f"),
            "taxatie_verandering_pct": st.column_config.NumberColumn("taxatie t.o.v. vorig jaar %", format="%.1f"),
        },
    )

# --------------------------------------------------------------------------
st.header("Stap 3 · Samenvoegen")
st.caption("Eén basistabel gemeente × jaar. Vertrekpunt is een vast raster van 42 rijen; elke bron wordt eraan "
           "gehangen met een left join, zodat er nooit een gemeente-jaar stil verdwijnt (rij 86). "
           "Opgeslagen in data/verwerkt/ met `python pipeline.py` (rij 88).")

leeg = basistabel.isna().sum()
with st.expander(f"Basistabel · {len(basistabel)} rijen × {basistabel.shape[1]} kolommen", expanded=True):
    st.dataframe(stappentabel(stappen3), hide_index=True)
    st.markdown(
        f"- **Lege vakken:** " + (", ".join(f"`{k}` {v}" for k, v in leeg[leeg > 0].items()) or "geen")
        + " — taxatie bestaat niet voor Guardamar en Pilar (< 25.000 inwoners); de markering "
        "`taxatie_tegenstrijdig` is daar en in 2019 (geen vorig jaar) leeg = niet te controleren (rij 89)\n"
        f"- **Markering `taxatie_tegenstrijdig`:** {int(basistabel['taxatie_tegenstrijdig'].sum())} rijen — "
        "vraagprijs en taxatie bewegen in tegengestelde richting; extra opzoeken (rij 85)\n"
        "- **lat / lon** = centrum van de gemeente; de kustdistricten hebben een eigen kaartpunt (rij 92)\n"
        "- **verkopen_per_1000** = aantal verkopen ÷ inwoners op 1/1 van hetzelfde jaar × 1.000 (rij 58)"
    )
    st.dataframe(
        basistabel.drop(columns="ine_code"), hide_index=True,
        column_config={
            "jaar": st.column_config.NumberColumn(format="%d"),
            "prijs_m2": st.column_config.NumberColumn("vraagprijs €/m²", format="%.0f"),
            "verkopen_per_1000": st.column_config.NumberColumn("verkopen per 1.000 inw.", format="%.1f"),
            "taxatiewaarde_m2": st.column_config.NumberColumn("taxatie €/m²", format="%.0f"),
        },
    )

with st.expander(f"Kustdistricten apart · {len(districten)} rijen (enkel vraagprijs, rij 87)"):
    st.markdown("4 districten × 7 jaar. Geen verkopen of inwoners per district. Op het dashboard: apart lijntje "
                "in de prijsgrafiek en een eigen stip op de kaart (rij 91–92).")
    st.dataframe(districten, hide_index=True,
                 column_config={"jaar": st.column_config.NumberColumn(format="%d"),
                                "prijs_m2": st.column_config.NumberColumn("vraagprijs €/m²", format="%.0f")})

# --------------------------------------------------------------------------
st.header("Stap 4 · Berekenen")
st.caption("Stijging jaar op jaar (rij 96) en van 2019 naar 2025 (rij 22), voor de vraagprijs, het aantal verkopen "
           "en de verkopen per 1.000 inwoners (rij 94); voor de kustdistricten enkel de vraagprijs (rij 95). "
           "Ontbreekt een waarde, dan blijft de stijging leeg (rij 40). Opgeslagen in data/verwerkt/ (rij 97).")

basistabel4, districten4, stijging = stap4()

with st.expander(f"Stijging 2019 → 2025 · {len(stijging)} rijen (6 gemeentes + 4 kustdistricten)", expanded=True):
    st.markdown(
        "- **Formule:** (waarde 2025 ÷ waarde 2019 − 1) × 100\n"
        "- **Per 1.000 inwoners** corrigeert voor de bevolkingsgroei: hoe *in trek* is een gemeente, los van haar groei (rij 94)\n"
        "- **Kustdistricten:** enkel vraagprijs; verkopen en inwoners bestaan niet per district"
    )
    st.dataframe(
        stijging, hide_index=True,
        column_config={
            "prijs_m2_2019": st.column_config.NumberColumn("prijs 2019 €/m²", format="%.0f"),
            "prijs_m2_2025": st.column_config.NumberColumn("prijs 2025 €/m²", format="%.0f"),
            "prijs_m2_stijging_pct": st.column_config.NumberColumn("prijs stijging", format="%+.1f %%"),
            "aantal_verkopen_2019": st.column_config.NumberColumn("verkopen 2019", format="%d"),
            "aantal_verkopen_2025": st.column_config.NumberColumn("verkopen 2025", format="%d"),
            "aantal_verkopen_stijging_pct": st.column_config.NumberColumn("verkopen stijging", format="%+.1f %%"),
            "verkopen_per_1000_2019": st.column_config.NumberColumn("per 1.000 inw. 2019", format="%.1f"),
            "verkopen_per_1000_2025": st.column_config.NumberColumn("per 1.000 inw. 2025", format="%.1f"),
            "verkopen_per_1000_stijging_pct": st.column_config.NumberColumn("per 1.000 inw. stijging", format="%+.1f %%"),
        },
    )

with st.expander("Jaar op jaar · extra kolommen in de basistabel (42 rijen) en de kustdistricten (28 rijen)"):
    st.markdown(
        "- **Formule:** (waarde dit jaar ÷ waarde vorig jaar − 1) × 100; 2019 is leeg (geen vorig jaar)\n"
        "- Toont of de stijging versnelt of afvlakt, en het effect van corona (rij 22, 96)"
    )
    st.dataframe(
        basistabel4[["gemeente", "jaar", "prijs_m2", "prijs_m2_jaar_pct", "aantal_verkopen", "aantal_verkopen_jaar_pct",
                     "verkopen_per_1000", "verkopen_per_1000_jaar_pct"]],
        hide_index=True,
        column_config={
            "jaar": st.column_config.NumberColumn(format="%d"),
            "prijs_m2": st.column_config.NumberColumn("prijs €/m²", format="%.0f"),
            "prijs_m2_jaar_pct": st.column_config.NumberColumn("prijs t.o.v. vorig jaar", format="%+.1f %%"),
            "aantal_verkopen": st.column_config.NumberColumn("verkopen", format="%d"),
            "aantal_verkopen_jaar_pct": st.column_config.NumberColumn("verkopen t.o.v. vorig jaar", format="%+.1f %%"),
            "verkopen_per_1000": st.column_config.NumberColumn("per 1.000 inw.", format="%.1f"),
            "verkopen_per_1000_jaar_pct": st.column_config.NumberColumn("per 1.000 t.o.v. vorig jaar", format="%+.1f %%"),
        },
    )
    st.markdown("**Kustdistricten** (enkel vraagprijs):")
    st.dataframe(
        districten4[["district", "gemeente", "jaar", "prijs_m2", "prijs_m2_jaar_pct"]], hide_index=True,
        column_config={
            "jaar": st.column_config.NumberColumn(format="%d"),
            "prijs_m2": st.column_config.NumberColumn("prijs €/m²", format="%.0f"),
            "prijs_m2_jaar_pct": st.column_config.NumberColumn("prijs t.o.v. vorig jaar", format="%+.1f %%"),
        },
    )
