# Woningprijzen Costa Blanca Zuid

Studieproject (Syntra, opleiding Data Scientist). Hoe verhouden de zes kustgemeentes van de Costa Blanca Zuid
(Elche, Guardamar del Segura, Orihuela, Pilar de la Horadada, Santa Pola en Torrevieja) zich tot elkaar qua
vraagprijs per m², aantal verkochte tweedehandswoningen en prijsevolutie tussen 2019 en 2025?
Zie `mission_statement_v2.md` voor het volledige doel.

## Bronnen

De ruwe bestanden staan in `data/ruw/` en worden nooit aangepast. De verwerking gebeurt in `pipeline.py`.

| # | Bron | Wat | Bestand in `data/ruw/` | Opgehaald |
|---|---|---|---|---|
| 1 | Idealista | Vraagprijs per m² per maand (01/2006–10/2026) | `idealista_*.txt` (10 bestanden) | 2026-11-07, met de hand gekopieerd |
| 2 | Ministerio de Vivienda, tabel 2.4 | Aantal verkochte tweedehandswoningen per kwartaal, per gemeente | `ministerio_2.4_tweedehands_per_gemeente_34010250.xls` | 2026-11-05, download |
| 3 | Ministerio de Vivienda, tabel 4 | Taxatiewaarde per m² per kwartaal (gemeentes > 25.000 inwoners), enkel als controle | `ministerio_tabel4_valor_tasado_gemeentes_25000_35103500.xls` | 2026-11-05, download |
| 4 | INE, tabel 2856 (Padrón) | Inwoners per gemeente op 1 januari | `ine_2856_inwoners.csv` | 2026-11-07, met `ophalen_bronnen.py` |
| 5 | Wikidata + OpenStreetMap | Kaartpunten (coördinaten) van de gemeentes en kustdistricten | `wikidata_coordinaten.csv` | 2026-11-08, met `ophalen_bronnen.py` |

### 1. Idealista — vraagprijs per m²

- Historiek van de vraagprijs per gemeente of district (*informes de precio de vivienda, histórico*).
- Geen downloadknop: de tabel werd op de website geselecteerd, gekopieerd en in een tekstbestand geplakt.
- Opgelet: een **vraagprijs** is wat de verkoper vraagt, niet wat de koper betaalt.

| Bestand | Gebied | Link |
|---|---|---|
| `idealista_guardamar.txt` | Guardamar del Segura | https://www.idealista.com/sala-de-prensa/informes-precio-vivienda/venta/comunitat-valenciana/alicante/guardamar-del-segura/historico/ |
| `idealista_elche.txt` | Elche | *link nog aan te vullen* |
| `idealista_orihuela.txt` | Orihuela | *link nog aan te vullen* |
| `idealista_pilar.txt` | Pilar de la Horadada | *link nog aan te vullen* |
| `idealista_santa_pola.txt` | Santa Pola | *link nog aan te vullen* |
| `idealista_torrevieja.txt` | Torrevieja | *link nog aan te vullen* |
| `idealista_orihuela_costa.txt` | Orihuela Costa (district) | *link nog aan te vullen* |
| `idealista_elche_arenales.txt` | Arenales del Sol (district Elche) | *link nog aan te vullen* |
| `idealista_elche_la_marina.txt` | La Marina (district Elche) | *link nog aan te vullen* |
| `idealista_elche_el_altet.txt` | El Altet – Balsares (district Elche) | *link nog aan te vullen* |

### 2. Ministerio de Vivienda — tabel 2.4, tweedehandsverkopen

- *Transacciones inmobiliarias de vivienda de segunda mano por municipios*, per kwartaal, 2004-Q1 t/m 2026-Q2.
- Oorsprong van de cijfers: notariële aktes (Consejo General del Notariado).
- Bestand: https://apps.fomento.gob.es/BoletinOnline2/sedal/34010250.XLS
- Lijst van tabellen: https://apps.fomento.gob.es/BoletinOnline2/?nivel=2&orden=34000000

### 3. Ministerio de Vivienda — tabel 4, taxatiewaarde (controle)

- *Valor tasado medio de vivienda libre de los municipios mayores de 25.000 habitantes*, €/m², één tabblad per kwartaal.
- Enkel voor gemeentes met meer dan 25.000 inwoners: Guardamar del Segura en Pilar de la Horadada ontbreken.
- Bestand: https://apps.fomento.gob.es/BoletinOnline2/sedal/35103500.XLS
- Lijst van tabellen: https://apps.fomento.gob.es/BoletinOnline2/?nivel=2&orden=35000000

### 4. INE — tabel 2856, inwoners

- *Cifras Oficiales de Población de los Municipios Españoles: Revisión del Padrón Municipal*,
  tabel 2856 *Alicante/Alacant: Población por municipios y sexo*.
- Webpagina: https://www.ine.es/jaxiT3/Tabla.htm?t=2856
- API (gebruikt door `ophalen_bronnen.py`): https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/2856?nult=8&tip=A

### 5. Wikidata + OpenStreetMap — kaartpunten

- Gemeentes: het Wikidata-item met de INE-gemeentecode (eigenschap P772), coördinaten uit eigenschap P625.
- Kustdistricten: Wikidata-item van de woonkern; La Marina staat niet in Wikidata en komt uit OpenStreetMap.
- Per punt staat de bron en het nummer (`bron_id`) in het csv-bestand, bv. Elche = https://www.wikidata.org/wiki/Q10509,
  La Marina = https://www.openstreetmap.org/node/390185380
- Wikidata-API: https://www.wikidata.org/w/api.php — OpenStreetMap (Nominatim): https://nominatim.openstreetmap.org/

## Bekeken maar niet gebruikt

- **INE IPV en ETDP**: prijsindex en aantal verkopen, maar niet per gemeente (fijnste niveau = provincie).
  Lijst van tabellen: https://servicios.ine.es/wstempus/js/ES/TABLAS_OPERACION/IPV
- Meer uitleg over elke bron: `data-exploratie.md`. Keuzes en waarom: `beslissingslog.md`.

## Bronnen opnieuw ophalen

```
conda activate syntra-ds
python ophalen_bronnen.py              (INE + kaartpunten)
python pipeline.py                     (verwerkte tabellen in data/verwerkt/)
streamlit run app.py
```

De bestanden van Idealista en het Ministerie moeten met de hand opnieuw opgehaald worden (zie de links hierboven).
