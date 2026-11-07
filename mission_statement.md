# Mission statement — Woningprijzen Costa Blanca Zuid

*Versie 1 (concept) — 2026-11-02. Elke keuze verwijst naar een rij in `beslissingslog.md`.*

## Doel

We willen een bestaand appartement kopen aan de Costa Blanca Zuid om het zelf enkele weken per jaar te gebruiken en de rest van het jaar aan toeristen te verhuren (rij 10).
Deze eerste analyse geeft **een beeld van de woningprijzen** in de kustgemeentes: waar is het duur, waar wordt veel verkocht en waar stijgen de prijzen (rij 18).
Verhuur, regelgeving en rendement komen in een later deel van de opdracht.

## Hoofdvraag

> **Hoe verhouden de zes kustgemeentes van de Costa Blanca Zuid zich tot elkaar qua prijs per m², aantal verkopen en prijsevolutie van bestaande appartementen tussen 2019 en 2025?**

## Analysevragen

| # | Vraag | Maatstaf | Bewerking | Brainstorm |
|---|---|---|---|---|
| **V1** | Wat was de gemiddelde verkoopprijs per m² van een bestaand appartement in elke kustgemeente, per jaar van 2019 tot 2025? | prijs/m² | niveau | vraag 1 |
| **V2** | Welke kustgemeentes zijn het duurst, op basis van de prijs per m² in 2025? | prijs/m² | rangschikken | vraag 2 |
| **V3** | Hoeveel bestaande appartementen werden per gemeente per jaar verkocht, absoluut en per 1.000 inwoners? | aantal verkopen | niveau + rangschikken | vraag 3 |
| **V4** | In welke kustgemeentes stegen de prijs per m² en het aantal verkopen het sterkst: over de hele periode 2019→2025 (in %) en van jaar tot jaar (incl. het effect van corona)? | prijs/m², aantal verkopen | verandering in de tijd | vraag 4 |
| *info* | Hoeveel Belgen wonen er in elke gemeente? (telt niet mee in de rangschikking) | Belgische inwoners | niveau | vraag 6 |

Elke vraag krijgt een **eigen rangschikking**; er is geen gecombineerde score (rij 31).

## Afbakening

| Wat zit erin | Keuze | Rij |
|---|---|---|
| Gebied | Santa Pola, Elche, Guardamar del Segura, Torrevieja, Orihuela, Pilar de la Horadada — als hele gemeente; kustzones van Elche en Orihuela later als de data het toelaat | 9, 24 |
| Woning | Bestaande appartementen (geen nieuwbouw), prijs per m² in plaats van "2 slaapkamers" | 12, 26 |
| Periode | 2019–2025, per jaar; kwartalen als extra rond corona | 11, 27 |
| Vergelijking | De zes gemeentes onderling (geen provincie of Spanje als referentie) | 21 |

**Bewust niet in deze analyse:** verhuurbezetting en -opbrengst, regelgeving rond toeristische verhuur, huurprijs, kosten en netto rendement (rij 17, 18), aanbod/leegloop (idee voor later), binnenlandse gemeentes (rij 9).

## Data

| Bron | Gebruik | Rij |
|---|---|---|
| Portal Estadístico del Notariado | **Hoofdbron**: echte verkoopprijs per m² en aantal verkopen | 25 |
| Ministerio de Vivienda — valor tasado | **Controle**: taxatiewaarde per m² (enkel gemeentes > 25.000 inwoners) | 25 |
| INE Padrón | Inwoners (voor "per 1.000 inwoners") en Belgische inwoners (info) | 13, 23 |

Eerst gratis bronnen; een betalende bron pas als dat nodig blijkt (rij 15).

## Werkwijze (algoritme)

1. **Ophalen** — Notariaat, Ministerie, INE Padrón.
2. **Controleren** — ontbrekende gemeente-jaren oplijsten (niet stil opvullen); gemeente-jaren met **minder dan 30 verkopen** markeren als onbetrouwbaar (rij 29); Notariaat en Ministerie vergelijken.
3. **Samenvoegen** — één tabel *gemeente × jaar* (6 × 7 = 42 rijen).
4. **Berekenen** — prijsniveau en rang, % stijging 2019→2025, jaarlijkse stijging; idem voor aantal verkopen.
5. **Tonen** — rangschikkingstabel, lijngrafiek prijs/m², staafdiagram stijging, kwartaalgrafiek rond corona.
6. **Besluiten** — antwoord op V1–V4, met de beperkingen erbij.

(rij 28)

## Beperkingen (vooraf gekend)

- **Gemeente ≠ kust**: de cijfers van Elche en Orihuela tellen ook hun binnenland mee.
- **Inwoners als benadering**: veel eigenaars aan de kust zijn niet ingeschreven, dus "per 1.000 inwoners" en "Belgen" zijn benaderingen.
- **Kleine aantallen**: na het weglaten van nieuwbouw kunnen kleine gemeentes minder dan 30 verkopen per jaar hebben.
- **Bronnen nog niet geopend**: alles hierboven steunt op zoekresultaten. Stap 2b moet bevestigen dat het Notariaat per gemeente teruggaat tot 2019, kan filteren op appartement en op nieuwbouw/bestaand, kwartalen en kleinere zones toont, en downloadbaar is; en voor welke gemeentes het Ministerie cijfers heeft. Valt iets tegen, dan passen we deze mission statement aan.
