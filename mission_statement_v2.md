# Mission statement — Woningprijzen Costa Blanca Zuid

*Versie 2 (concept) — 2026-11-07. Vervangt versie 1 (`mission_statement.md`, 2026-11-02) na het dashboardontwerp en de data-exploratie (stap 2b). Elke keuze verwijst naar een rij in `beslissingslog.md`.*

## Doel

We willen een bestaand appartement kopen aan de Costa Blanca Zuid om het zelf enkele weken per jaar te gebruiken en de rest van het jaar aan toeristen te verhuren (rij 10).
Deze eerste analyse geeft **een beeld van de woningprijzen** in de kustgemeentes: waar is het duur, waar wordt veel verkocht en waar stijgen de prijzen (rij 18).
Verhuur, regelgeving en rendement komen in een later deel van de opdracht.

## Hoofdvraag

> **Hoe verhouden de zes kustgemeentes van de Costa Blanca Zuid zich tot elkaar qua vraagprijs per m², aantal verkochte tweedehandswoningen en prijsevolutie tussen 2019 en 2025?**

## Analysevragen

| # | Vraag | Maatstaf | Bewerking | Element |
|---|---|---|---|---|
| **V1** | Wat was de gemiddelde vraagprijs per m² in elke kustgemeente, per jaar van 2019 tot 2025? | vraagprijs/m² | niveau | E2, E6, E8 |
| **V2** | Welke kustgemeentes zijn het duurst, op basis van de vraagprijs per m² in 2025? | vraagprijs/m² | vergelijken (grafiek gesorteerd van hoog naar laag) | E2, E6, E8 |
| **V3** | Hoeveel tweedehandswoningen werden per gemeente per jaar verkocht, absoluut en per 1.000 inwoners? | aantal verkopen | niveau + vergelijken | E4, E6 |
| **V4** | In welke kustgemeentes stegen de vraagprijs per m² en het aantal verkopen het sterkst: over de hele periode 2019→2025 (in %) en van jaar tot jaar (incl. het effect van corona)? | vraagprijs/m², aantal verkopen | verandering in de tijd | E3, E4, E5 |

Geen rangnummers en geen gecombineerde score: de grafieken worden van hoog naar laag gesorteerd (rij 37, herziet rij 31). "Duurste" wordt bepaald op 2025 (rij 30).

## Afbakening

| Wat zit erin | Keuze | Rij |
|---|---|---|
| Gebied | Santa Pola, Elche, Guardamar del Segura, Torrevieja, Orihuela, Pilar de la Horadada — als **hele gemeente** | 9, 24, 65 |
| Kustdistricten (extra info) | Elche: Arenales del Sol, La Marina, El Altet – Balsares (apart getoond, niet samengevoegd) · Orihuela: Orihuela Costa — enkel vraagprijs, naast het cijfer van de hele gemeente | 65, 66, 67 |
| Woning | **Tweedehandswoningen** (appartement + huis): het Ministerie splitst per gemeente niet in appartement/huis. Voorkeur blijft appartementen als dat ooit kan | 26, 51 |
| Prijs | **Vraagprijs** per m² (Idealista), niet de echte verkoopprijs | 68 |
| Periode | 2019–2025, per jaar (maanden → jaar: gemiddelde van 12 maanden); kwartalen als extra rond corona | 27, 70 |
| Vergelijking | De zes gemeentes onderling (geen provincie of Spanje als referentie) | 21, 59 |

**Bewust niet in deze analyse:** verhuurbezetting en -opbrengst, regelgeving rond toeristische verhuur, huurprijs, kosten en netto rendement (rij 17, 18), aanbod/leegloop (idee voor later), binnenlandse gemeentes (rij 9), **Belgische inwoners** (geen cijfers per gemeente gevonden, voorlopig laten rusten — rij 55).

## Data

| Bron | Gebruik | Status | Rij |
|---|---|---|---|
| **B6 Idealista** — informes precio vivienda (histórico) | **Werkbron prijs**: vraagprijs/m² per maand, per gemeente en per kustdistrict | ✅ overgenomen en gecontroleerd (2019–2025 volledig) | 57, 64, 68, 70 |
| **B3 Ministerio** — tabel 2.4 | **Aantal verkopen** van tweedehandswoningen per gemeente, per kwartaal | ⚠️ bruikbaar met beperking | 50, 51 |
| **B4 INE Padrón** — tabel 2856 | **Inwoners** per gemeente (voor "per 1.000 inwoners"); verkopen jaar X ↔ telling 1/1 jaar X+1 | ✅ bruikbaar | 54, 58 |
| **B2 Ministerio** — tabel 4 (valor tasado) | **Controle**: taxatiewaarde/m² (gemiddelde van 4 kwartalen), enkel 4 van de 6 gemeentes | ⚠️ controle | 48, 56, 63 |
| **B7 Wikidata** (+ OpenStreetMap) | **Coördinaten** voor de kaart; ~~Elche en Orihuela = kustkern~~ herzien: centrum van elke gemeente + eigen stip per kustdistrict | ✅ bruikbaar | 61, 62, 92 |
| B1 Notariado | Echte verkoopprijzen — **vervangt Idealista als het op tijd antwoordt** | ⚠️ geblokkeerd, mail 05/11 zonder antwoord | 49, 53, 68 |
| B5 INE prijsindex | — | ❌ niet per gemeente | 59 |

## Werkwijze (algoritme)

1. **Ophalen** — Idealista (10 tekstbestanden), Ministerie (2 Excelbestanden), INE (inwoners), Wikidata (coördinaten).
2. **Controleren** — ontbrekende gemeente-jaren oplijsten (niet stil opvullen, rij 40); Idealista vergelijken met de taxatiewaarde van het Ministerie (4 van 6 gemeentes): verschil in % tonen + tegengestelde richting markeren (rij 77, 78). *(De drempel van 30 verkopen vervalt — rij 81.)*
3. **Samenvoegen** — één tabel *gemeente × jaar* (6 × 7 = 42 rijen) + kustdistricten als extra.
4. **Berekenen** — prijsniveau, % stijging 2019→2025, jaarlijkse stijging; idem voor aantal verkopen; verkopen per 1.000 inwoners.
5. **Tonen** — dashboard volgens rij 34–41: conclusies, kerncijfers, kaart, lijngrafiek prijs, staafdiagram stijging, lijngrafiek verkopen, kwartaalgrafiek corona (uitklapblok); grafieken gesorteerd, geen rangnummers.
6. **Besluiten** — antwoord op V1–V4, met de beperkingen erbij.

(rij 28; in de app wordt elke stap zichtbaar met rijen in/uit — opdracht stap 3)

## Beperkingen (vooraf gekend)

- **Vraagprijs ≠ verkoopprijs**: Idealista toont wat verkopers vragen, niet wat kopers betalen (rij 68).
- **Prijs en verkopen gaan niet over exact dezelfde woningen**: de vraagprijs komt van te koop staande woningen bij Idealista (woningtype niet vermeld), de verkopen van het Ministerie (alle tweedehandswoningen).
- **Gemeente ≠ kust**: de cijfers van Elche en Orihuela tellen ook hun binnenland mee; de kustdistricten tonen enkel de vraagprijs (rij 24, 65).
- **Kleine districten schommelen**: La Marina en El Altet hebben sprongen van meer dan 5 % per maand, vermoedelijk door weinig aanbod.
- **Controle beperkt**: de taxatiewaarde bestaat enkel voor 4 van de 6 gemeentes (geen Guardamar en Pilar de la Horadada).
- **Inwoners als benadering**: veel eigenaars aan de kust zijn niet ingeschreven, dus "per 1.000 inwoners" is een benadering.
