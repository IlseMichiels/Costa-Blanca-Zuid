"""Tabblad 1 van de app: het dashboard (ontwerp: beslissingslog rij 34-41, 91-92, 99-105).

Leest enkel de bewaarde CSV's uit data/verwerkt (rij 90 punt 4, rij 100), zodat het meteen opent.
Volgorde op het scherm (rij 38, herzien in rij 106): titel + hoofdvraag · kerncijfers · kaart ·
prijsgrafiek naast staafdiagram stijging · verkopengrafiek · coronagrafiek (gewoon zichtbaar, rij 108) ·
conclusies + beperkingen.
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

import pipeline as pl

# --------------------------------------------------------------------------
# Kleuren en vaste volgorde
# --------------------------------------------------------------------------
BLAUW, ZAND, GRIJS = "#0B4F6C", "#E9D8B4", "#9AA5AE"     # thema Middellandse Zee (rij 104)

# Gemeentes van noord naar zuid langs de kust (rij 105.1). Elke gemeente houdt overal dezelfde kleur
# (rij 104), ook als je andere gemeentes uitvinkt. Palet nagekeken op kleurenblindheid.
KLEUREN = {
    "Elche": "#2a78d6",
    "Santa Pola": "#eb6834",
    "Guardamar del Segura": "#1baf7a",
    "Orihuela": "#eda100",
    "Torrevieja": "#e87ba4",
    "Pilar de la Horadada": "#008300",
}
VOLGORDE = list(KLEUREN)
VAN, TOT = pl.PERIODE

CSS = """
<style>
.hero {background: linear-gradient(135deg, #0B4F6C 0%, #1C7293 100%); padding: 1.6rem 2rem;
       border-radius: 16px; margin-bottom: .6rem;}
.hero h1 {color: #FFFFFF; font-size: 2.1rem; margin: 0 0 .5rem 0; padding: 0;}
.hero p {color: #E8EFF3; margin: 0; font-size: 1.05rem; max-width: 60rem;}
.hero .onder {color: #E9D8B4; font-size: .85rem; margin-top: .8rem;}
.kaartje {background: #FFFFFF; border: 1px solid #E6E1D6; border-top: 5px solid var(--kleur);
          border-radius: 12px; padding: .9rem 1rem; box-shadow: 0 1px 4px rgba(11, 79, 108, .08);
          margin-bottom: .5rem;}
.kaartje .naam {font-weight: 600; color: #1F2A33; font-size: .95rem; margin-bottom: .35rem;}
.kaartje .prijs {font-size: 1.65rem; font-weight: 700; color: #0B4F6C; line-height: 1.1;}
.kaartje .eenheid {font-size: .8rem; color: #5B6770; font-weight: 400;}
.kaartje .regel {font-size: .85rem; color: #3A4650; margin-top: .45rem;}
.kaartje .regel b {color: #1F2A33;}
.badge {display: inline-block; background: #E9D8B4; color: #5A4413; font-size: .72rem; font-weight: 700;
        padding: .12rem .55rem; border-radius: 999px; letter-spacing: .05em; vertical-align: middle;}
.sectie {font-size: 1.25rem; font-weight: 600; color: #0B4F6C; margin: 1.2rem 0 .1rem 0;}
.uitleg {font-size: .88rem; color: #5B6770; margin-bottom: .4rem;}
</style>
"""


# --------------------------------------------------------------------------
# Getallen in Belgische notatie (rij 80, punt 7)
# --------------------------------------------------------------------------
def heel(x):
    """1234.5 -> '1.235'"""
    return f"{x:,.0f}".replace(",", ".")


def komma(x, d=1):
    """12.34 -> '12,3'"""
    return f"{x:,.{d}f}".replace(",", " ").replace(".", ",").replace(" ", ".")


def pct(x):
    """79.51 -> '+79,5 %'"""
    return f"{'+' if x >= 0 else '−'}{komma(abs(x))} %"


# --------------------------------------------------------------------------
# Data (bewaard door `python pipeline.py`)
# --------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def lees(naam):
    return pl.lees_verwerkt(f"{naam}.csv")


def data():
    basis = lees("basistabel")
    districten = lees("kustdistricten")
    stijging = lees("stijging")
    kwartalen = lees("kwartalen")
    return basis, districten, stijging, kwartalen


# --------------------------------------------------------------------------
# Opmaak van de grafieken: rustig, één stijl voor alle figuren
# --------------------------------------------------------------------------
def stijl(fig, hoogte=380, legende=True):
    fig.update_layout(
        template="plotly_white", height=hoogte, separators=",.",          # komma = decimaal, punt = duizendtal
        font=dict(family="Source Sans Pro, sans-serif", size=13, color="#1F2A33"),
        margin=dict(l=10, r=10, t=10, b=10), hovermode="x unified",
        showlegend=legende,
        legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="left", x=0, font=dict(size=12)),
        hoverlabel=dict(bgcolor="white", font_size=12),
    )
    fig.update_xaxes(showgrid=False, linecolor="#C9CFD4", ticks="outside", tickcolor="#C9CFD4")
    fig.update_yaxes(gridcolor="#EEF0F2", zeroline=False)
    return fig


def toon_figuur(fig):
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


# --------------------------------------------------------------------------
# 1 · Titel en hoofdvraag
# --------------------------------------------------------------------------
def titel():
    st.markdown(
        f"""<div class="hero">
        <h1>Woningprijzen Costa Blanca Zuid</h1>
        <p>Hoe verhouden de zes kustgemeentes zich tot elkaar qua <b>vraagprijs per m²</b>,
        <b>aantal verkochte tweedehandswoningen</b> en <b>prijsevolutie</b> tussen {VAN} en {TOT}?</p>
        <div class="onder">6 kustgemeentes · 4 kustdistricten · {VAN}–{TOT} ·
        bronnen: Idealista, Ministerio de Vivienda, INE</div>
        </div>""",
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------
# 2 · Conclusies en beperkingen (E7) — altijd alle 6 gemeentes (rij 41)
# --------------------------------------------------------------------------
def conclusies(basis, stijging, kwartalen):
    """Concepttekst (rij 101): de cijfers worden uit de data berekend, de zinnen zijn een voorstel."""
    j_tot = basis[basis["jaar"] == TOT].set_index("gemeente")
    gem = stijging[stijging["soort"] == "gemeente"].set_index("gemeente")
    dist = stijging[stijging["soort"] == "kustdistrict"].set_index("district")
    duur, goedkoop = j_tot["prijs_m2"].idxmax(), j_tot["prijs_m2"].idxmin()
    midden = j_tot["prijs_m2"].drop([duur, goedkoop])
    duurste_dist = dist["prijs_m2_2025"].idxmax()

    p = gem["prijs_m2_stijging_pct"]
    jaar_pct = basis.pivot(index="jaar", columns="gemeente", values="prijs_m2_jaar_pct")
    vroeg, laat = jaar_pct.loc[VAN + 1:VAN + 2], jaar_pct.loc[TOT - 1:TOT]

    v = j_tot["aantal_verkopen"]
    v1000 = j_tot["verkopen_per_1000"]
    groei_v = gem["aantal_verkopen_stijging_pct"].sort_values(ascending=False)

    per_jaar = basis.groupby("jaar")["aantal_verkopen"].sum()
    per_kw = kwartalen.groupby("periode")["aantal_verkopen"].sum()
    lockdown = (per_kw["2020 K2"] / per_kw["2019 K2"] - 1) * 100
    jaar2020 = (per_jaar[2020] / per_jaar[2019] - 1) * 100
    jaar2021 = (per_jaar[2021] / per_jaar[2019] - 1) * 100
    prijs2020 = jaar_pct.loc[2020]

    links, rechts = st.columns([3, 2], gap="large")
    with links:
        st.markdown('<div class="sectie">Conclusies <span class="badge">CONCEPT · nog na te lezen</span></div>',
                    unsafe_allow_html=True)
        st.markdown(
            f"- **Prijsniveau (V1, V2):** in {TOT} is **{duur}** het duurst ({heel(j_tot.loc[duur, 'prijs_m2'])} €/m²) "
            f"en **{goedkoop}** het goedkoopst ({heel(j_tot.loc[goedkoop, 'prijs_m2'])} €/m²). De andere vier liggen "
            f"dicht bij elkaar ({heel(midden.min())}–{heel(midden.max())} €/m²). Aan de kust is het duurder dan in de "
            f"hele gemeente: **{duurste_dist}** vraagt {heel(dist.loc[duurste_dist, 'prijs_m2_2025'])} €/m².\n"
            f"- **Prijsstijging (V4):** alle zes stegen sterk, van {pct(p.min())} ({p.idxmin()}) tot "
            f"{pct(p.max())} ({p.idxmax()}) tussen {VAN} en {TOT}. De stijging **versnelt**: in {VAN + 1}–{VAN + 2} "
            f"lag de stijging per jaar tussen {pct(vroeg.min().min())} en {pct(vroeg.max().max())}, "
            f"in {TOT - 1}–{TOT} tussen {pct(laat.min().min())} en {pct(laat.max().max())}.\n"
            f"- **Verkopen (V3):** **{v.idxmax()}** verkoopt het meest ({heel(v.max())} woningen in {TOT}, "
            f"{komma(v1000.loc[v.idxmax()])} per 1.000 inwoners). {v1000.idxmin()} verkoopt absoluut veel "
            f"({heel(v.loc[v1000.idxmin()])}), maar per 1.000 inwoners het minst ({komma(v1000.min())}). "
            f"Het aantal verkopen steeg het sterkst in **{groei_v.index[0]}** ({pct(groei_v.iloc[0])}) en "
            f"**{groei_v.index[1]}** ({pct(groei_v.iloc[1])}).\n"
            f"- **Corona (V4):** in het 2e kwartaal van 2020 (lockdown) zakte het aantal verkopen met "
            f"{komma(abs(lockdown), 0)} % tegenover een jaar eerder (6 gemeentes samen), over heel 2020 met "
            f"{komma(abs(jaar2020))} %. In 2021 lag het al {komma(jaar2021)} % hoger dan in 2019. De vraagprijs "
            f"bleef in 2020 nagenoeg gelijk ({pct(prijs2020.min())} tot {pct(prijs2020.max())})."
        )
    with rechts:
        st.markdown('<div class="sectie">Beperkingen</div>', unsafe_allow_html=True)
        st.markdown(
            "- **Vraagprijs ≠ verkoopprijs:** Idealista toont wat verkopers vragen, niet wat kopers betalen.\n"
            "- **Prijs en verkopen gaan niet over exact dezelfde woningen** (te koop bij Idealista ↔ alle "
            "verkochte tweedehandswoningen).\n"
            "- **Gemeente ≠ kust:** Elche en Orihuela tellen ook hun binnenland mee; de kustdistricten tonen "
            "enkel de vraagprijs.\n"
            "- **Kleine districten schommelen** (La Marina, El Altet), vermoedelijk door weinig aanbod.\n"
            "- **Inwoners als benadering:** veel eigenaars aan de kust zijn niet ingeschreven.\n"
            "- **Controle beperkt:** de taxatiewaarde bestaat enkel voor 4 van de 6 gemeentes."
        )


# --------------------------------------------------------------------------
# 3 · Kerncijfers (E6): één kaartje per gemeente (rij 102) — veranderen niet mee met de filters
# --------------------------------------------------------------------------
def kaartjes(basis, stijging):
    st.markdown(f'<div class="sectie">Kerncijfers {TOT}</div>', unsafe_allow_html=True)
    j_tot = basis[basis["jaar"] == TOT].set_index("gemeente")
    gem = stijging[stijging["soort"] == "gemeente"].set_index("gemeente")
    kolommen = st.columns(len(VOLGORDE))
    for kolom, g in zip(kolommen, VOLGORDE):
        prijs = j_tot.loc[g, "prijs_m2"]
        groei = gem.loc[g, "prijs_m2_stijging_pct"]
        per1000 = j_tot.loc[g, "verkopen_per_1000"]
        # ontbrekende waarde: "geen data", niets opvullen (rij 40)
        prijs_txt = f'{heel(prijs)} <span class="eenheid">€/m²</span>' if pd.notna(prijs) else "geen data"
        groei_txt = pct(groei) if pd.notna(groei) else "geen data"
        per1000_txt = komma(per1000) if pd.notna(per1000) else "geen data"
        with kolom:
            st.markdown(
                f"""<div class="kaartje" style="--kleur: {KLEUREN[g]}">
                <div class="naam">{g}</div>
                <div class="prijs">{prijs_txt}</div>
                <div class="regel"><b>{groei_txt}</b> sinds {VAN}</div>
                <div class="regel"><b>{per1000_txt}</b> verkopen per 1.000 inw.</div>
                </div>""",
                unsafe_allow_html=True,
            )


# --------------------------------------------------------------------------
# 4 · Kaart (E8): stip per gemeente + kleinere stip per kustdistrict (rij 35, 36, 91, 92)
# --------------------------------------------------------------------------
def kaart(basis, districten, stijging, gekozen):
    st.markdown('<div class="sectie">Kaart van de kust</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="uitleg">Op de stip: vraagprijs {TOT}. Ga met de muis over een stip voor de andere '
                'cijfers. Grote stip = hele gemeente (centrum), kleine stip = kustdistrict.</div>',
                unsafe_allow_html=True)
    gem = stijging[stijging["soort"] == "gemeente"]
    g = basis[(basis["jaar"] == TOT) & basis["gemeente"].isin(gekozen)].merge(
        gem[["gemeente", "prijs_m2_stijging_pct", "aantal_verkopen_stijging_pct"]], on="gemeente")
    d = districten[(districten["jaar"] == TOT) & districten["gemeente"].isin(gekozen)].merge(
        stijging[stijging["soort"] == "kustdistrict"][["district", "prijs_m2_stijging_pct"]], on="district")

    def kleur(df):        # grijs = geen data (rij 40)
        return [KLEUREN[gm] if pd.notna(p) else GRIJS for gm, p in zip(df["gemeente"], df["prijs_m2"])]

    def label(df):
        return [f"{heel(p)} €" if pd.notna(p) else "geen data" for p in df["prijs_m2"]]

    def tekst(x, f):
        return f(x) if pd.notna(x) else "geen data"

    fig = go.Figure()
    # witte rand onder elke stip, zodat stippen los van de achtergrond en van elkaar staan
    for df, maat in [(g, 22), (d, 13)]:
        fig.add_trace(go.Scattermap(lat=df["lat"], lon=df["lon"], mode="markers", hoverinfo="skip",
                                    marker=dict(size=maat + 4, color="white"), showlegend=False))
    fig.add_trace(go.Scattermap(
        lat=g["lat"], lon=g["lon"], mode="markers+text", text=label(g), textposition="middle right",
        textfont=dict(size=13, color="#1F2A33"), marker=dict(size=22, color=kleur(g)), showlegend=False,
        hovertext=[f"<b>{r.gemeente}</b> (hele gemeente)<br>Vraagprijs {TOT}: {tekst(r.prijs_m2, heel)} €/m²"
                   f"<br>Prijs {VAN}→{TOT}: {tekst(r.prijs_m2_stijging_pct, pct)}"
                   f"<br>Verkopen {TOT}: {tekst(r.aantal_verkopen, heel)} ({tekst(r.verkopen_per_1000, komma)} per 1.000 inw.)"
                   f"<br>Verkopen {VAN}→{TOT}: {tekst(r.aantal_verkopen_stijging_pct, pct)}"
                   for r in g.itertuples()],
        hoverinfo="text"))
    fig.add_trace(go.Scattermap(
        lat=d["lat"], lon=d["lon"], mode="markers+text", text=label(d), textposition="middle right",
        textfont=dict(size=11, color="#3A4650"), marker=dict(size=13, color=kleur(d)), showlegend=False,
        hovertext=[f"<b>{r.district}</b> (kustdistrict van {r.gemeente})<br>Vraagprijs {TOT}: "
                   f"{tekst(r.prijs_m2, heel)} €/m²<br>Prijs {VAN}→{TOT}: {tekst(r.prijs_m2_stijging_pct, pct)}"
                   "<br><i>geen verkopen per district</i>" for r in d.itertuples()],
        hoverinfo="text"))
    fig.update_layout(map=dict(style="carto-positron", center=dict(lat=38.07, lon=-0.70), zoom=9.2),
                      height=480, margin=dict(l=0, r=0, t=0, b=0), hoverlabel=dict(bgcolor="white", font_size=12))
    toon_figuur(fig)


# --------------------------------------------------------------------------
# 5 · Prijs per m² (E2) naast stijging 2019 -> 2025 (E3)
# --------------------------------------------------------------------------
def prijsgrafiek(basis, districten, gekozen):
    st.markdown('<div class="sectie">Vraagprijs per m²</div>', unsafe_allow_html=True)
    st.markdown('<div class="uitleg">Volle lijn = hele gemeente, stippellijn = kustdistrict in de kleur van de '
                'gemeente. Een onderbroken lijn = geen data.</div>', unsafe_allow_html=True)
    fig = go.Figure()
    for g in gekozen:
        df = basis[basis["gemeente"] == g]
        fig.add_trace(go.Scatter(x=df["jaar"], y=df["prijs_m2"], name=g, mode="lines+markers",
                                 line=dict(color=KLEUREN[g], width=2.5), marker=dict(size=7),
                                 connectgaps=False, hovertemplate="%{y:,.0f} €/m²"))
        for dnaam, dd in districten[districten["gemeente"] == g].groupby("district", sort=False):
            fig.add_trace(go.Scatter(x=dd["jaar"], y=dd["prijs_m2"], name=f"{dnaam} (kust)", mode="lines",
                                     line=dict(color=KLEUREN[g], width=2, dash="dash"),
                                     connectgaps=False, hovertemplate="%{y:,.0f} €/m²"))
    stijl(fig, hoogte=430)
    fig.update_yaxes(title=None, ticksuffix=" €")
    fig.update_xaxes(dtick=1)
    toon_figuur(fig)


def stijgingsgrafiek(stijging, gekozen):
    st.markdown(f'<div class="sectie">Prijsstijging {VAN} → {TOT}</div>', unsafe_allow_html=True)
    st.markdown('<div class="uitleg">Van hoog naar laag; boven de gemeentes, onder de kustdistricten '
                '(rij 103).</div>', unsafe_allow_html=True)
    s = stijging[stijging["gemeente"].isin(gekozen)]
    gem = s[s["soort"] == "gemeente"].sort_values("prijs_m2_stijging_pct", ascending=False, na_position="last")
    dist = s[s["soort"] == "kustdistrict"].sort_values("prijs_m2_stijging_pct", ascending=False, na_position="last")
    dist_namen = dist["district"] + " (" + dist["gemeente"] + ")"          # gemeente tussen haakjes (rij 107)
    groepen = [(gem, gem["gemeente"], "Gemeentes", 1.0), (dist, dist_namen, "Kustdistricten", 0.7)]
    groepen = [gr for gr in groepen if len(gr[0])]
    fig = make_subplots(rows=len(groepen), cols=1, shared_xaxes=True, vertical_spacing=0.12,
                        row_heights=[len(gr[0]) for gr in groepen], subplot_titles=[gr[2] for gr in groepen])
    for rij, (df, namen, _, dekking) in enumerate(groepen, start=1):
        waarden = df["prijs_m2_stijging_pct"]
        fig.add_trace(go.Bar(
            x=waarden.fillna(0), y=namen, orientation="h", marker=dict(color=[KLEUREN[g] for g in df["gemeente"]],
                                                                        opacity=dekking),
            text=[pct(w) if pd.notna(w) else "geen data" for w in waarden], textposition="outside",
            cliponaxis=False, showlegend=False,
            hovertemplate="%{y}: %{text}<extra></extra>"), row=rij, col=1)
        fig.update_yaxes(autorange="reversed", row=rij, col=1)
    stijl(fig, hoogte=430, legende=False)
    fig.update_layout(hovermode="closest", bargap=0.35)
    fig.update_xaxes(ticksuffix=" %", range=[0, stijging["prijs_m2_stijging_pct"].max() * 1.22], gridcolor="#EEF0F2",
                     showgrid=True)
    fig.update_yaxes(gridcolor="rgba(0,0,0,0)")
    fig.update_annotations(font=dict(size=13, color="#5B6770"), x=0, xanchor="left")
    toon_figuur(fig)


# --------------------------------------------------------------------------
# 6 · Aantal verkopen (E4): absoluut of per 1.000 inwoners (rij 41)
# --------------------------------------------------------------------------
def verkopengrafiek(basis, gekozen, maat):
    kolom, eenheid = (("aantal_verkopen", "verkopen") if maat == "absoluut aantal"
                      else ("verkopen_per_1000", "per 1.000 inw."))
    st.markdown(f'<div class="sectie">Verkochte tweedehandswoningen — {maat}</div>', unsafe_allow_html=True)
    st.markdown('<div class="uitleg">Kies in de zijbalk absoluut of per 1.000 inwoners. Per 1.000 inwoners toont hoe '
                '<i>in trek</i> een gemeente is, los van haar grootte. Geen cijfers per kustdistrict.</div>',
                unsafe_allow_html=True)
    fig = go.Figure()
    for g in gekozen:
        df = basis[basis["gemeente"] == g]
        fig.add_trace(go.Scatter(x=df["jaar"], y=df[kolom], name=g, mode="lines+markers",
                                 line=dict(color=KLEUREN[g], width=2.5), marker=dict(size=7), connectgaps=False,
                                 hovertemplate=f"%{{y:,.{0 if kolom == 'aantal_verkopen' else 1}f}} {eenheid}"))
    stijl(fig, hoogte=400)
    fig.update_xaxes(dtick=1)
    toon_figuur(fig)


# --------------------------------------------------------------------------
# 7 · Corona per kwartaal (E5) (rij 79, 105.5); geen uitklapblok meer (rij 108)
# --------------------------------------------------------------------------
def coronagrafiek(kwartalen, gekozen):
    """Gewoon zichtbaar, geen uitklapblok meer (rij 108, herziet rij 38)."""
    st.markdown('<div class="sectie">Corona van dichterbij: verkopen en vraagprijs per kwartaal</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="uitleg">De lichte band = 2e kwartaal 2020 (lockdown in Spanje). '
                'Enkel de 6 gemeentes; geen kwartaalcijfers per kustdistrict (rij 82).</div>',
                unsafe_allow_html=True)
    perioden = list(dict.fromkeys(kwartalen["periode"]))
    lockdown = perioden.index("2020 K2")
    kol1, kol2 = st.columns(2, gap="large")
    for kolom, (waarde, titel, fmt) in zip(
            [kol1, kol2], [("aantal_verkopen", "Aantal verkopen", ",.0f"), ("prijs_m2", "Vraagprijs €/m²", ",.0f")]):
        fig = go.Figure()
        for g in gekozen:
            df = kwartalen[kwartalen["gemeente"] == g]
            fig.add_trace(go.Scatter(x=df["periode"], y=df[waarde], name=g, mode="lines",
                                     line=dict(color=KLEUREN[g], width=2), connectgaps=False,
                                     hovertemplate=f"%{{y:{fmt}}}"))
        fig.add_vrect(x0=lockdown - 0.5, x1=lockdown + 0.5, fillcolor=ZAND, opacity=0.6, line_width=0,
                      layer="below")
        stijl(fig, hoogte=340)
        fig.update_xaxes(tickangle=-45, tickvals=[p for p in perioden if p.endswith("K1")],
                         ticktext=[p[:4] for p in perioden if p.endswith("K1")])
        with kolom:
            st.markdown(f"**{titel}**")
            toon_figuur(fig)


# --------------------------------------------------------------------------
# Zijbalk en geheel
# --------------------------------------------------------------------------
def filters():
    """Filters in de zijbalk (rij 41): gemeentes aan/uit en verkopen absoluut of per 1.000 inwoners."""
    st.sidebar.markdown("### Filters")
    st.sidebar.caption("Werken op de kaart en de grafieken. De kerncijfers en conclusies tonen altijd alle "
                       f"6 gemeentes, {VAN}–{TOT}.")
    st.sidebar.markdown("**Gemeentes** (noord → zuid)")
    gekozen = [g for g in VOLGORDE if st.sidebar.checkbox(g, value=True, key=f"filter_{g}")]
    maat = st.sidebar.radio("**Verkopen tonen als**", ["absoluut aantal", "per 1.000 inwoners"], key="filter_maat")
    st.sidebar.divider()
    st.sidebar.caption("Kustdistricten horen bij hun gemeente: vink je Elche of Orihuela uit, dan verdwijnen "
                       "ook hun kustdistricten.")
    return gekozen, maat


def toon():
    """Tekent het volledige dashboard."""
    st.markdown(CSS, unsafe_allow_html=True)
    basis, districten, stijging, kwartalen = data()
    gekozen, maat = filters()

    titel()
    kaartjes(basis, stijging)

    if gekozen:
        kaart(basis, districten, stijging, gekozen)
        links, rechts = st.columns([3, 2], gap="large")
        with links:
            prijsgrafiek(basis, districten, gekozen)
        with rechts:
            stijgingsgrafiek(stijging, gekozen)
        verkopengrafiek(basis, gekozen, maat)
        coronagrafiek(kwartalen, gekozen)
    else:
        st.info("Vink in de zijbalk minstens één gemeente aan om de kaart en de grafieken te zien.")

    # conclusies + beperkingen onderaan (rij 106, herziet rij 38); altijd alle 6 gemeentes (rij 41)
    st.divider()
    conclusies(basis, stijging, kwartalen)
    st.caption("Bronnen en werkwijze: zie het tabblad *Data en pijplijn* en README.md. "
               "Elke keuze verwijst naar een rij in beslissingslog.md.")
