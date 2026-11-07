# Spec-prompt — Woningprijzen Costa Blanca Zuid

*Stap 2 van de opdracht (Project 1). Concept 2026-11-07, opgesteld met de AI op basis van `mission_statement_v2.md`, `data-exploratie.md` en `beslissingslog.md`; nagekeken en aangepast door Ilse.*

---

## De prompt

Ik bouw een Streamlit-app die de zes kustgemeentes van de Costa Blanca Zuid (Santa Pola, Elche, Guardamar del Segura, Torrevieja, Orihuela, Pilar de la Horadada) met elkaar vergelijkt op **vraagprijs per m²**, **aantal verkochte tweedehandswoningen** en **prijsevolutie**, van 2019 tot en met 2025. Doel en afbakening staan in `mission_statement_v2.md`; elke keuze staat met een rijnummer in `beslissingslog.md`. Lees die twee bestanden eerst.

**Wat ik nu wil (tegen 10/11): stap 3 — de pijplijn.** Het eigenlijke dashboard (grafieken, kaart, conclusies) komt later.

### 1. Invoer (staat al in `data/ruw/`, nooit aanpassen)

| Gegeven | Bestand(en) | Vorm |
|---|---|---|
| Vraagprijs/m² per maand (Idealista) | `idealista_<gemeente>.txt` (6 gemeentes) en `idealista_orihuela_costa.txt`, `idealista_elche_arenales.txt`, `idealista_elche_la_marina.txt`, `idealista_elche_el_altet.txt` (kustdistricten) | tab-gescheiden tekst, 1 kop + 250 maanden (01/2006–10/2026). Spaans (`Octubre 2026`, `1.934 €/m2`, `n.d.`), behalve Torrevieja: Nederlands (`Oktober 2026`, `€2.566/m2`, `en` = leeg) |
| Aantal tweedehandsverkopen per kwartaal (Ministerio, tabel 2.4) | `ministerio_2.4_tweedehands_per_gemeente_34010250.xls` | 1 tabblad, alle gemeentes van Spanje, kwartalen 2004–2026 |
| Taxatiewaarde/m² per kwartaal (Ministerio, tabel 4) — enkel controle | `ministerio_tabel4_valor_tasado_gemeentes_25000_35103500.xls` | 86 tabbladen (1 per kwartaal); kolom "meer dan 5 jaar"; let op de lege kolom tussen prijzen en aantallen; enkel Elche, Orihuela, Santa Pola, Torrevieja |
| Inwoners op 1 januari (INE tabel 2856) | nog geen bestand — cijfers staan in `data-exploratie.md` (B4) | — |
| Coördinaten (Wikidata) | nog geen bestand — staan in `data-exploratie.md` (B7) | — |

### 2. Bouw

- **`pipeline.py`** met **pure functies**: één functie per stap, invoer = DataFrame(s), uitvoer = DataFrame; geen Streamlit-imports, geen globale toestand.
- **`app.py`** dat elke stap toont in een eigen `st.expander`: **hoeveel rijen erin en eruit gaan**, **waarom rijen wegvallen**, en **een voorbeeld van de data na de stap**.
- **Bovenaan een rijen-trechter** die in één oogopslag toont waar data verdwijnt.
- Inlezen met caching (`st.cache_data`).

### 3. Stappen van de pijplijn (algoritme uit de mission statement, rij 28)

1. **Ophalen** — de Idealista-bestanden, beide Ministerie-bestanden, inwoners en coördinaten inlezen in een lange tabel (gemeente/district × periode).
2. **Controleren**
   - beperken tot 2019–2025;
   - ontbrekende gemeente-jaren **oplijsten, niet opvullen** (rij 40);
   - *(drempel van 30 verkopen vervalt — rij 81)*;
   - Idealista vergelijken met de taxatiewaarde (4 van 6 gemeentes) als controle.
3. **Samenvoegen** — één basistabel *gemeente × jaar* = 6 × 7 = **42 rijen**, met de kolommen `gemeente | jaar | prijs_m2 | aantal_verkopen | inwoners | verkopen_per_1000 | taxatiewaarde_m2 | lat | lon` + markeringen; de kustdistricten als aparte tabel (enkel prijs).
4. **Berekenen** — % stijging 2019→2025 en jaarlijkse % stijging, voor prijs en aantal verkopen.

### 4. Afspraken die al vastliggen

- Prijs per jaar = **gemiddelde van de 12 maanden** (rij 70); taxatiewaarde per jaar = **gemiddelde van de 4 kwartalen** (rij 63).
- Verkopen per jaar = **som van de 4 kwartalen**; kwartalen apart bewaren voor de coronagrafiek (E5).
- Inwoners: verkopen van jaar X ↔ telling van **1/1 van jaar X+1**; bestaat 1/1/2026 nog niet, dan **1/1 van jaar X voor alle jaren** — geen mengvorm (rij 58).
- Kustdistricten **apart**, nooit samengevoegd (rij 65–67); hoofdcijfer = hele gemeente.
- Ontbrekende waarden worden **nooit** opgevuld (rij 40).
- Windows, conda-environment `syntra-ds`; installeer niets zonder te vragen.

**Stel me eerst een vraag op elke plek waar je zelf een aanname zou maken. Begin pas met bouwen als alle vragen beantwoord zijn.**
