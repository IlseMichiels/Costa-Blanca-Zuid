# Data-exploratie — Costa Blanca Zuid

Stap 2b: welke data bestaat er, hoe betrouwbaar is ze, en hoe komen we van de bronnen tot het
dashboard uit `Brainstorming.txt` (beslissingen rij 33–41)?

Gestart: 2026-11-04. Beslissingen hierover komen in `beslissingslog.md`, het verloop in `proces.txt`.

**Statuslegende:** ⬜ nog niet gecontroleerd · ✅ gecontroleerd en bruikbaar · ⚠️ bruikbaar met beperking · ❌ niet bruikbaar

---

## 1. Welke data hebben we nodig? (vanuit het dashboard)

| Nodig voor | Gegeven | Niveau | Periode |
|---|---|---|---|
| E2, E3, E6, E7, E8 | prijs per m² van bestaande appartementen (echte verkoopprijs) | gemeente × jaar | 2019–2025 |
| E5 | prijs per m² van bestaande appartementen | gemeente × kwartaal | 2019–2025 |
| E4, E6, E8, drempel < 30 | aantal verkochte bestaande appartementen | gemeente × jaar | 2019–2025 |
| E4 (per 1.000), E8 | aantal inwoners | gemeente × jaar | 2019–2025 |
| E8 (info) | aantal Belgische inwoners | gemeente × jaar | 2019–2025 (of minstens 2025) |
| E8 | coördinaten (punt op de kust) | gemeente | — |
| controle (stap 2c) | taxatiewaarde per m² | gemeente × jaar | 2019–2025 |

## 2. Kandidaat-bronnen

> Alles in deze tabel komt voorlopig uit de **kennis van de AI en eerdere zoekresultaten**. Niets is
> nog geopend. Elke regel krijgt pas een ✅, ⚠️ of ❌ nadat we de bron echt bekeken hebben.

| # | Bron | Wat het (vermoedelijk) levert | Niveau (vermoedelijk) | Soort cijfer | Status |
|---|---|---|---|---|---|
| B1 | Portal Estadístico del Notariado | prijs/m² + aantal verkopen, filter op woningtype | gemeente, misschien postcode | echte verkoopprijs (akte bij notaris) | ⚠️ site geblokkeerd (05/11) |
| B2 | Ministerio de Vivienda — *valor tasado*, tabel 4 | taxatiewaarde €/m² (tot 5 jaar / meer dan 5 jaar / totaal) + aantal taxaties, per kwartaal | gemeentes > 25.000 inwoners (4 van onze 6) | schatting door taxateur | ⚠️ bruikbaar als controle, 4 van 6 (05/11) |
| B3 | Ministerio de Vivienda — *transacciones inmobiliarias* | aantal verkopen per kwartaal, nieuwbouw vs. tweedehands | alle gemeentes | uit notariële aktes (Consejo General del Notariado) | ⚠️ bruikbaar met beperking (05/11) |
| B4 | INE — Cifras oficiales de población (Padrón), tabel 2856 | inwoners (totaal, man/vrouw) op 1 januari | gemeente × jaar | officiële bevolkingsregistratie | ✅ bruikbaar (05/11) |
| B5 | INE — prijsindex (IPV) en transmisiones (ETDP) | prijsindex, aantal overdrachten | IPV: regio (CCAA); ETDP: provincie — **geen gemeente** | officieel | ❌ niet bruikbaar (06/11) |
| B6 | Idealista — informes precio vivienda (histórico) | vraagprijs/m², vanaf januari 2006 | gemeente (alle 6 gevonden) | **vraag**prijs, geen verkoopprijs | ✅ werkbron voor de prijs (07/11, rij 68); Notariaat vervangt als het op tijd antwoordt |
| B7 | Coördinaten — Wikidata (via INE-gemeentecode) + OpenStreetMap (La Marina) | lengte- en breedtegraad per gemeente en per kustdistrict | gemeente (centrum) + 4 kustdistricten (herzien 08/11, rij 92) | geografisch | ✅ bruikbaar (07/11, herzien 08/11) |

## 3. Controlelijst per bron

*(wordt ingevuld tijdens het openen van de bronnen)*

### B1 — Portal Estadístico del Notariado

> ⚠️ **Site geblokkeerd op 2026-11-05**: melding "Web Page Blocked" op de laptop thuis (Telenet)
> én op de gsm via mobiele data; ook de AI kreeg een foutmelding (HTTP 502). De blokkering zit bij
> de site zelf. Oorzaak onbekend (enkel buiten Spanje? tijdelijke storing?). Later opnieuw proberen
> (rij 49).

**Kliklijst** (samengevoegd met de eerste controlelijst, 2026-11-05). Open www.penotariado.com in
je browser en begin met **Elche** (grootste gemeente, meeste verkopen). 📷 = maak een screenshot.

**A. Periode — eerst controleren**
- [ ] 📷 Toont de kaart enkel "de laatste 12 maanden", of kun je een **jaar** kiezen (bv. 2019)?
- [ ] 📷 Is er een **evolutiegrafiek** of tabel per jaar voor één gemeente? (zoek *evolución*, *histórico*, *estadísticas*)
- [ ] Gaat het per gemeente terug tot **2019**? Vanaf welk jaar begint het?
- [ ] Zijn er ook **kwartalen** (nodig voor E5, corona)?

**B. Filters**
- [ ] Welke keuzes staan er bij *tipo de finca*? Noteer de exacte woorden (*piso*, *plurifamiliar*, …).
- [ ] Filter op **tweedehands** (*segunda mano* / *usada*) vs. nieuwbouw?
- [ ] Inzoomen tot **postcode**? Probeer Orihuela Costa (03189) en Elche-kust, bv. Arenales del Sol (03195).

**C. Cijfers**
- [ ] Staan **prijs/m²** én **aantal verkopen** er allebei?
- [ ] Gemiddelde (*medio*) of mediaan (*mediana*) prijs/m²?
- [ ] Wat zie je bij een kleine zone met weinig verkopen: een getal, een leeg vak of een waarschuwing?

**D. Gebruik**
- [ ] 📷 Is er een knop om te **downloaden** (*descargar*, *exportar*, CSV, Excel), of enkel op het scherm?
- [ ] Is er een pagina **metodología** of **preguntas frecuentes**? Noteer de link.

**Later (als we de cijfers hebben)**
- [ ] Hoeveel gemeente-jaren hebben < 30 verkopen?

**Bevindingen B1 (2026-11-05) — ⚠️ nog niet zelf gecontroleerd in het portaal**

> Bron van deze bevindingen: het persbericht van het Notariaat (23/10/2025) en krantenartikels.
> De site www.penotariado.com zelf gaf een storing (HTTP 502) en is nog niet bekeken.

Wat het portaal volgens die bronnen biedt: echte verkoopprijzen uit notariële aktes, gratis,
elke maand bijgewerkt. Cijfers: prijs/m², gemiddelde oppervlakte, gemiddelde totaalprijs,
aantal verkopen.

1. ✅ (te bevestigen) **Filter tweedehands + appartement** (*construcción*: nieuw/tweedehands;
   *tipo de finca*: o.a. *plurifamiliar*) — past bij rij 26 (enkel bestaande appartementen).
2. ✅ (te bevestigen) **Filter op postcode** — kan de open vraag uit rij 24 oplossen
   (Elche-kust en Orihuela Costa apart).
3. ⚠️ **Grootste risico: de periode.** De kaart toont "de laatste 12 maanden". Het persbericht
   vermeldt ook "estadísticas completas de los últimos 12 años", maar niet waar of hoe. Kunnen
   we per gemeente niet per jaar 2019–2025 opvragen, dan missen we de basis voor E2, E3, E4 en
   E5. **Als eerste controleren.**
4. ❓ **Onbekend:** downloadbaar of overtikken? Wat toont het portaal bij weinig verkopen
   (belangrijk voor de drempel van 30, rij 29)?

Gevolg: het Ministerie (B2/B3) wordt belangrijker als controle, en mogelijk als reservebron
als het Notariaat geen jaarreeksen per gemeente heeft.

### B2 / B3 — Ministerio de Vivienda
- [x] Voor welke van de 6 gemeentes zijn er cijfers? → B3: alle 6. B2 (taxatie): 4 van de 6 (Elche, Orihuela, Santa Pola, Torrevieja); Guardamar en Pilar ontbreken (< 25.000 inwoners)
- [x] Periode en tijdseenheid? → B3: per kwartaal, 2004-Q1 t/m 2026-Q2
- [x] Downloadbaar? → ja, Excel (.xls)

**Bevindingen B3 (2026-11-05) — bestand zelf bekeken**

> Bestand: `data/ruw/ministerio_2.4_tweedehands_per_gemeente_34010250.xls` (6,5 MB), gedownload op
> 2026-11-05 van https://apps.fomento.gob.es/BoletinOnline2/sedal/34010250.XLS — tabel 2.4
> *"Transacciones inmobiliarias de vivienda de segunda mano por municipios"*. Ruw bestand: nooit aanpassen.
> Oorsprong van de cijfers: notariële aktes, beheerd door het Consejo General del Notariado
> (bron: jaarboek Regio Murcia 2022, hoofdstuk 15). Tabellenlijst: https://apps.fomento.gob.es/BoletinOnline2/?nivel=2&orden=34000000

- Eén tabblad; aantal tweedehandsverkopen **per kwartaal**, 2004-Q1 t/m 2026-Q2. Enkel 2026-Q2 is voorlopig; **2019–2025 is definitief**.
- ± 8.100 rijen = **alle gemeentes van Spanje** (geen inwonersdrempel).
- **Alle 6 gemeentes aanwezig**, 90/90 kwartalen ingevuld, geen tekst of lege vakken.

Aantal tweedehandsverkopen per jaar (som van de 4 kwartalen, berekend door de AI):

| Gemeente | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|
| Elche/Elx | 2.516 | 2.038 | 3.104 | 3.313 | 3.116 | 3.340 | 3.233 |
| Guardamar del Segura | 606 | 447 | 713 | 986 | 1.005 | 1.106 | 1.082 |
| Orihuela | 2.895 | 2.152 | 3.041 | 4.478 | 3.993 | 4.317 | 4.188 |
| Pilar de la Horadada | 576 | 493 | 829 | 951 | 873 | 928 | 1.012 |
| Santa Pola | 1.273 | 956 | 1.557 | 1.829 | 1.668 | 1.772 | 1.661 |
| Torrevieja | 4.485 | 2.998 | 4.566 | 7.237 | 6.524 | 6.686 | 6.154 |

1. ✅ Dekt **E4** (aantal verkopen per jaar) en **E5** (kwartalen, corona). De dip in 2020 is overal zichtbaar.
2. ✅ De drempel van 30 verkopen (rij 29) wordt nooit gehaald: kleinste kwartaal 2019–2025 = 55. → drempel **vervalt** (rij 81, 07/11).
3. ⚠️ **Alle tweedehandswoningen** (appartement + huis, vrij + sociaal), geen appartementen apart. Per gemeente bestaat die splitsing niet bij het Ministerie (enkel per regio/provincie). → **aanvaard (rij 51)**.
4. ⚠️ Enkel **aantallen**, geen echte prijs per m². Gemiddelde verkoopwaarde (tabel 3.3) en splitsing appartement/huis (tabel 1.5) bestaan enkel per regio/provincie.
5. 🔍 Controle: de 6 rijen horen bij de provincie Alicante (er bestaan ook bv. "Elche de la Sierra" en "Orihuela del Tremedal"). Nog **niet** gecontroleerd: of de som van de gemeentes klopt met het provinciale totaal.

**Bevindingen B2 (2026-11-05) — bestand zelf bekeken**

> Bestand: `data/ruw/ministerio_tabel4_valor_tasado_gemeentes_25000_35103500.xls` (4,0 MB), gedownload
> op 2026-11-05 van https://apps.fomento.gob.es/BoletinOnline2/sedal/35103500.XLS — tabel 4
> *"Valor tasado medio de vivienda libre de los municipios mayores de 25.000 habitantes"*.
> Tabellenlijst: https://apps.fomento.gob.es/BoletinOnline2/?nivel=2&orden=35000000. Ruw bestand: nooit aanpassen.

- 86 tabbladen, **één per kwartaal**, 2005-Q1 t/m 2026-Q2. Eenheid: euro/m².
- Per gemeente: taxatiewaarde **tot 5 jaar** / **meer dan 5 jaar** / totaal, plus het **aantal taxaties** per groep. Opgelet: tussen de prijzen en de aantallen staat een **lege kolom**.
- "n.r" = vermoedelijk *no representativo* (te weinig taxaties); komt bij onze gemeentes 2019–2025 niet voor.
- **4 van de 6 gemeentes**, volledig (28/28 kwartalen): Elche, Orihuela, Santa Pola, Torrevieja. Guardamar en Pilar de la Horadada ontbreken.

Taxatiewaarde woningen **ouder dan 5 jaar**, **4e kwartaal**, €/m²:

| Gemeente | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|
| Elche/Elx | 953 | 968 | 1.020 | 1.012 | 1.155 | 1.299 | 1.540 |
| Orihuela | 1.133 | 1.126 | 1.297 | 1.232 | 1.428 | 1.592 | 1.851 |
| Santa Pola | 1.322 | 1.393 | 1.476 | 1.560 | 1.745 | 1.938 | 2.318 |
| Torrevieja | 1.249 | 1.208 | 1.294 | 1.408 | 1.571 | 1.808 | 2.122 |

Aantal taxaties > 5 jaar per jaar: 652 (Santa Pola 2020) tot 2.515 (Elche 2025); kleinste kwartaal: 120.

1. ✅ **"Meer dan 5 jaar"** komt dicht bij tweedehands (niet exact: een woning van 3 jaar kan ook tweedehands zijn). Als controle zuiverder dan het totaal.
2. ⚠️ **Controle voor 4 van de 6 gemeentes**; geen controlecijfer voor Guardamar en Pilar de la Horadada.
3. ⚠️ Taxatiewaarde stijgt 60–75 % tussen 2019 en 2025 — geen verkoopprijs, wel een eerste idee van de richting.
4. ❓ Welk controlecijfer per jaar (4e kwartaal of gemiddelde van 4 kwartalen)? → open vraag, sectie 6.
5. 🔍 **Fout van de AI, verbeterd:** door de lege kolom werden de aantallen eerst één kolom te vroeg gelezen (ontdekt doordat Elche verdacht weinig taxaties had t.o.v. Almería). De prijzen waren juist. Het leesscript controleert nu of de lege kolom er staat.

### B4 — INE Padrón
- [x] Inwoners per gemeente per jaar 2019–2025? → ja, alle 6 gemeentes, 2018–2025
- [ ] Belgen per gemeente? → nog geen tabel gevonden; **voorlopig laten rusten (rij 55)**

**Bevindingen B4 (2026-11-05) — rechtstreeks bevraagd via de INE-API**

> Bron: INE, operatie 22 *"Cifras Oficiales de Población de los Municipios Españoles: Revisión del
> Padrón Municipal"*, tabel **2856** *"Alicante/Alacant: Población por municipios y sexo"*.
> Webpagina: https://www.ine.es/jaxiT3/Tabla.htm?t=2856 — API: https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/2856?nult=8&tip=A
> Nog niets bewaard in `data/ruw/` (enkel bekeken).

Inwoners op 1 januari:

| Gemeente | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|
| Elche/Elx | 232.517 | 234.765 | 234.205 | 235.580 | 238.293 | 243.128 | 245.557 |
| Guardamar del Segura | 15.348 | 15.849 | 15.983 | 16.138 | 17.328 | 18.111 | 18.564 |
| Orihuela | 77.414 | 78.505 | 78.940 | 80.784 | 82.449 | 83.720 | 84.560 |
| Pilar de la Horadada | 21.905 | 22.347 | 22.597 | 22.949 | 23.428 | 23.844 | 24.316 |
| Santa Pola | 32.306 | 33.303 | 34.148 | 36.174 | 37.816 | 38.556 | 39.709 |
| Torrevieja | 83.337 | 84.667 | 82.842 | 83.547 | 89.290 | 94.803 | 98.533 |

1. ✅ Volledig voor **E4 (verkopen per 1.000 inwoners)**: alle 6 gemeentes, 2019–2025, officieel, geen lege vakken.
2. ⚠️ **Teldatum = 1 januari.** Beslist (rij 58): verkopen van jaar X ↔ telling 1/1 van jaar X+1. Op 2026-11-06 is de laatste telling 1/1/2025 (1/1/2026 nog niet gepubliceerd) → bij stap 3 opnieuw nakijken; anders 1/1 van jaar X voor alle jaren.
3. 💡 Guardamar (18.564) en Pilar de la Horadada (24.316) hebben **minder dan 25.000 inwoners** → vallen vermoedelijk buiten de taxatiewaarden per gemeente (B2): geen controlecijfer voor die twee.
4. 🔍 Torrevieja: daling in 2021, daarna +15.000 inwoners sinds 2022 — geen fout, mogelijk interessant voor E7.
5. ❓ Belgen per gemeente: niet in deze tabel; voorlopig laten rusten.

### B5 — INE IPV / ETDP
- [x] Bestaat er iets op gemeenteniveau? → nee: ❌ voor dit project

**Bevindingen B5 (2026-11-06) — rechtstreeks bevraagd via de INE-API**

> Lijst van tabellen: https://servicios.ine.es/wstempus/js/ES/TABLAS_OPERACION/IPV en …/ETDP

1. ❌ **IPV** (tabellen 79540, 79541, 79563, 80270, 80271, 80272): een prijs*index* (stijging t.o.v. een basisjaar, geen €/m²), enkel voor heel Spanje en per regio (CCAA, bv. Comunitat Valenciana).
2. ❌ **ETDP** (tabellen 6150, 6155, 49280, compraventa de viviendas): aantal verkopen, ook tweedehands (*segunda mano*), maar fijnste niveau = **provincie** Alicante. 360 reeksen = 72 gebieden (Spanje, 19 regio's, 52 provincies) × 5 woningtypes; geen enkele gemeente.
3. Niet bewaard als context voor E7 (rij 59): het project vergelijkt de 6 gemeentes onderling.

### B6 — Vraagprijzen
- [x] Zijn vraagprijzen gratis per gemeente beschikbaar? → ja, bij Idealista (door Ilse bekeken op 05/11)

**Kliklijst Idealista** — open in je browser (de site blokkeert de AI, HTTP 403):
`https://www.idealista.com/sala-de-prensa/informes-precio-vivienda/venta/comunitat-valenciana/alicante/guardamar-del-segura/historico/`
- [x] Opent de pagina? Prijzen per m²? → ja
- [x] Vanaf welke maand/jaar? → januari 2006
- [x] Alle woningen (*vivienda*) of appartementen (*pisos*)? → niet vermeld op de pagina
- [x] Andere gemeentes te vinden? → ja
- [x] Per maand, per kwartaal of per jaar? → per maand
- [x] Downloadknop, of overtikken/kopiëren? → geen download; cijfers overnemen

**Bevindingen B6 (2026-11-05)**

> Door de AI geprobeerd: Idealista gaf HTTP 403, Fotocasa-adres gaf enkel de startpagina, RealAdvisor
> gaf enkel een momentopname (juli 2026) zonder reeks. **Idealista door Ilse zelf bekeken.**

1. ✅ Idealista: vraagprijs per m² per gemeente, **vanaf januari 2006**, onze gemeentes te vinden.
2. ⚠️ **Vraagprijs ≠ verkoopprijs**: wat de verkoper vraagt, niet wat de koper betaalt. Enkel als **reserve** voor de prijs als het Notariaat (B1) niet lukt (rij 25).
3. ❓ Woningtype niet vermeld (alle woningen of enkel appartementen?).
4. RealAdvisor: niet bruikbaar (geen reeks; vermoedelijk schattingsmodel).
5. ⚠️ **Per maand, geen download**: cijfers moeten met de hand overgenomen worden (kans op tikfouten → dubbel controleren).

**Bevindingen B6 (2026-11-07)** — Idealista is nu de **werkbron** voor de prijs (rij 68)

6. ✅ **Overgenomen** door de tabel "histórico" te kopiëren naar .txt in `data/ruw/` (rij 64): 6 gemeentes + kustdistricten Orihuela Costa, Arenales del Sol, La Marina, El Altet – Balsares (rij 65–67). Browservertaling uit (behalve Torrevieja: vertaald, prijzen wel gecontroleerd).
7. ✅ **Gecontroleerd** (AI-script, enkel lezen): elk bestand 250 maanden (01/2006–10/2026), geen dubbels of gaten; **2019–2025: 84/84 maanden met prijs** in alle 10 bestanden. Prijs t.o.v. maandvariatie van de site: 2 afwijkingen van 0,1 procentpunt (afronding).
8. ⚠️ **Schommelingen in kleine districten**: sprongen > 5 % per maand bij La Marina (5×), El Altet (1×) en Pilar (1×). Ze kloppen met de site (geen kopieerfout); vermoedelijk weinig woningen te koop.
9. ⚠️ De 3 kustdistricten van Elche liggen ver uit elkaar (2025: 1.824 – 3.150 €/m²) → apart tonen (rij 67).

### B7 — Coördinaten
- [x] Bron gekozen en 6 punten genoteerd → Wikidata (07/11)

| INE | Gemeente | Kaartpunt | lon | lat |
|---|---|---|---|---|
| 03065 | Elche | Los Arenales del Sol (kustkern) * | -0.5214 | 38.2531 |
| 03133 | Torrevieja | centrum | -0.6833 | 37.9778 |
| 03121 | Santa Pola | centrum | -0.5556 | 38.1897 |
| 03099 | Orihuela | Orihuela Costa (kustkern) * | -0.7535 | 37.9004 |
| 03076 | Guardamar del Segura | centrum | -0.6550 | 38.0897 |
| 03902 | Pilar de la Horadada | centrum | -0.7926 | 37.8675 |

\* Op het dashboard vermelden: "kaartpunt = kustkern; cijfers = hele gemeente" (rij 61).

**Bevindingen B7 (2026-11-07)**
1. ✅ Bron: Wikidata (opgezocht via INE-gemeentecode), gratis, enkel lezen.
2. ⚠️ Elche en Orihuela: hoofdkern ligt landinwaarts (~10 en ~25 km) → kustkern gekozen (rij 61).
3. Kaartpunt = centrum van de woonkern, geen strand (rij 62).

**Herziening B7 (2026-11-08, rij 91-92)** — de tabel en bevinding 2 hierboven gelden niet meer:
- Elche en Orihuela krijgen ook het **centrum** als kaartpunt (cijfers = hele gemeente, stip = gemeente).
- De **4 kustdistricten** krijgen een eigen stip (woonkern, geen strand, cf. rij 62):

| Gemeente | District | Kaartpunt | Bron | lon | lat |
|---|---|---|---|---|---|
| Elche | — | centrum | Wikidata Q10509 | -0.6983 | 38.2669 |
| Orihuela | — | centrum | Wikidata Q487786 | -0.9469 | 38.0856 |
| Elche | Arenales del Sol | woonkern Los Arenales del Sol | Wikidata Q9023882 | -0.5214 | 38.2531 |
| Elche | La Marina | woonkern la Marina | OpenStreetMap node 390185380 * | -0.6454 | 38.1464 |
| Elche | El Altet – Balsares | woonkern El Altet ** | Wikidata Q6746200 | -0.5392 | 38.2731 |
| Orihuela | Orihuela Costa | woonkern Orihuela Costa | Wikidata Q2803214 | -0.7535 | 37.9004 |

\* La Marina: Wikidata heeft enkel het strand (Q28121201), niet de woonkern → OpenStreetMap (rij 93).
\*\* Balsares heeft geen eigen kaartpunt in Wikidata; El Altet = hoofdkern van het district.
De 4 andere gemeentes: coördinaten ongewijzigd t.o.v. 07/11.

## 4. Betrouwbaarheid

*(per bron: wie maakt het, hoe wordt het gemeten, wat zijn de valkuilen — in te vullen)*

## 5. Van bron naar dashboard

*(welke bron levert welke kolom van de basistabel, en welke stappen zijn nodig — in te vullen na de controle)*

| Kolom basistabel | Bron | Bewerking | Element(en) |
|---|---|---|---|
| prijs_m2 | B6 Idealista, vraagprijs (hele gemeente; kustdistricten als extra info, rij 65–67) | maanden → jaar: gemiddelde van de 12 maanden (rij 70); maanden → kwartaal voor E5 | E2, E3, E5, E6, E8 |
| aantal_verkopen | B3 tabel 2.4 (tweedehands, alle woningen) | kwartalen optellen tot jaren; kwartalen apart houden voor E5 | E4, E5, E6, E8 |
| inwoners | B4 INE tabel 2856 (totaal, 1 januari) | verkopen jaar X ↔ telling 1/1 jaar X+1 (rij 58); is 1/1/2026 er niet bij stap 3 → 1/1 jaar X voor alle jaren | E4, E8 |
| verkopen_per_1000 | (berekend) | aantal_verkopen / inwoners × 1.000 | E4, E8 |
| belgen | | | E8 |
| taxatiewaarde_m2 | B2 tabel 4, kolom "meer dan 5 jaar" (4 van 6 gemeentes) | kwartalen → jaar: gemiddelde van de 4 kwartalen (rij 63) | controle |
| lat / lon | B7 Wikidata + OpenStreetMap (6 gemeentes + 4 districten, sectie 3) | geen; ~~Elche en Orihuela = kustkern + vermelding (rij 61)~~ herzien: centrum + eigen stip per district (rij 92) | E8 |

## 6. Gevolgen voor het ontwerp en de mission statement

*(wat valt tegen, en wat passen we aan)*

- **Tweedehandswoningen i.p.v. tweedehandsappartementen** (rij 51): op het dashboard en in de mission statement v2 "tweedehandswoningen" schrijven; beperking vermelden in E7.
- **Teldatum inwoners (B4): beslist in rij 58.** Einde van het jaar (1/1 van het jaar erna). Is de telling van 1/1/2026 er niet bij stap 3, dan begin van het jaar (1/1 van dat jaar) voor álle jaren — geen mengvorm.
- **Infovraag Belgen: voorlopig laten rusten** (rij 55); geen tabel per gemeente gevonden.
- **Controlecijfer per jaar uit B2 = gemiddelde van de 4 kwartalen** (rij 63, 07/11; herziet het uitstel van rij 60). Geen controle mogelijk voor Guardamar en Pilar de la Horadada.
- **Bron voor de prijs per m² per gemeente = Idealista (B6), vraagprijs** (rij 68, 07/11). Het Notariaat (B1) vervangt Idealista als het op tijd antwoordt met bruikbare verkoopprijzen. Op het dashboard vermelden: "vraagprijs, geen verkoopprijs".
  *(Historiek:)* het Notariaat (B1) was geblokkeerd; het Ministerie heeft per gemeente enkel taxatiewaarden (B2, enkel controle volgens rij 48).

  **Zoektocht prijs per m² (2026-11-05)** — online gezocht door de AI, nog niet zelf gecontroleerd:

  | Bron | Soort prijs | Per gemeente? | Appartementen apart? | Opmerking |
  |---|---|---|---|---|
  | Notariaat-portaal (B1) | echte verkoopprijs | ja, ook postcode | ja | geblokkeerd |
  | Registradores (ERI) | echte verkoopprijs | nee: regio, provincie, hoofdsteden | ? | officieel, vanaf 2007 |
  | Tinsa (IMIE Mercados Locales) | taxatiewaarde | ja, per kwartaal | ? | taxatiebedrijf |
  | Ministerie (B2) | taxatiewaarde | enkel > 25.000 inwoners | nee | enkel controle (rij 48) |
  | Idealista / RealAdvisor (B6) | vraagprijs | ja, ook postcode | ja | geen verkoopprijs |
  | CoHispania-kaart (datos.gob.es) | onduidelijk | ja | ? | stopt in 2021 |

  Conclusie: enige gevonden bron met **echte verkoopprijs per gemeente** = het Notariaat-portaal.
  Actie (rij 53): Ilse mailt het Notariaat en probeert het portaal later opnieuw. Lukt dat niet, dan
  volgt een afweging: echte prijs per provincie (Registradores) vs. taxatiewaarde per gemeente vs.
  vraagprijs per gemeente.
  Stand: mail verstuurd op 2026-11-05; op 2026-11-07 nog geen antwoord. Opvolgen rond 2026-11-12.
