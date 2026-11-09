# Zadania Lab 5 — model danych, walidacja i przegląd

Indeks zgłoszeń GitHub dla części C. Zasada: **mało i konkretnie** — każde zgłoszenie ma krótki cel, kryterium odbioru i właściciela. Zgłoszenia #1–#5 dotyczą istniejącej implementacji i nie są duplikowane w tym indeksie.

## Zgłoszenia Lab 5

| Issue | Cel | Właściciel | Kryterium odbioru | Status |
|---|---|---|---|---|
| [#6](https://github.com/kollekka/Marabuty/issues/6) | Pełny przetworzony zbiór i wersjonowanie migawki | kollekka (Adrian Świeca) | `prepare_data.py` daje 228 318 × 81, `quality_checks.py` PASS, SHA256 i `data_version` zapisane, brak nadpisania plików Lab 3–4 | otwarte |
| [#7](https://github.com/kollekka/Marabuty/issues/7) | Walidator danych treningowych: schemat, zakresy, filtr `Używane`, chronologia | MrKabas (Kacper Stopa) | Walidator wymaga kolumn `MODEL_FEATURES` + `price_pln`, sprawdza zakresy i skończoność, odrzuca `Nowość`, błąd przerywa trening, test na błędnym CSV | otwarte |
| [#8](https://github.com/kollekka/Marabuty/issues/8) | Metadane świeżości i wersjonowanie wyników | MrKabas (Kacper Stopa) | `data_version` i `generated_at` w wynikach albo `run.json`, opis w README/`experiment.md`, brak nadpisywania, spójność z `dataflow.mmd` | otwarte |
| [#9](https://github.com/kollekka/Marabuty/issues/9) | Przegląd UC-01 i kontraktu — niespójności F1–F6 | kollekka (Adrian Świeca) | F1–F4 poprawione albo jawnie przypisane, F5/F6 opisane, werdykt i właściciele zmian | otwarte |
| [#11](https://github.com/kollekka/Marabuty/issues/11) | Walidacja manifestu i plików wynikowych | MrKabas (Kacper Stopa) | Manifest: wymagane pola, `scope`, `target_transform`, kolejność `features`, `interval_coverage`; CSV: kolumny, typy, braki, klucze, skończoność; błąd = kod ≠ 0 i testy | otwarte |

## Zamknięte duplikaty

| Issue | Duplikat | Powód |
|---|---|---|
| [#10](https://github.com/kollekka/Marabuty/issues/10) | [#8](https://github.com/kollekka/Marabuty/issues/8) | Ten sam zakres: wersjonowanie uruchomień i ochrona wyników przed nadpisaniem. #8 jest szersze i już zawiera metadane świeżości. |
| [#12](https://github.com/kollekka/Marabuty/issues/12) | [#9](https://github.com/kollekka/Marabuty/issues/9) | Ten sam zakres: przegląd UC-01 i ujednolicenie nazw. Ustalenia C5 są w [`docs/reviews/uc-01.md`](../reviews/uc-01.md) i w komentarzu do #9. |

## Kolejność realizacji

1. **#6** — pełny plik przetworzony i `data_version` (wejście dla treningu).
2. **#7** — walidator danych treningowych (nie dopuszcza złych wierszy).
3. **#1** — trening Ridge i zapis artefaktu (istniejące zadanie).
4. **#11** — walidacja manifestu i wyników (spina #6, #7 i #1).
5. **#8** — metadane świeżości wyników ewaluacji.
6. **#9** — domknięcie przeglądu po poprawkach.

## Mapowanie na wymagania laboratorium

| Wymaganie | Rezultat |
|---|---|
| C1 — model logiczny | [`docs/data-model.md`](../data-model.md) — obiekty, znaczenie rekordu, relacje, ERD logiczny |
| C2 — model fizyczny | [`docs/data-model-physical.md`](../data-model-physical.md) — ścieżki, formaty, schematy pól, zasada braku nadpisań |
| C3 — ADR | [`docs/decisions/001-storage.md`](../decisions/001-storage.md) — decyzja, alternatywy, koszty, zespół, warunek ponownego rozważenia |
| C4 — zadania | ten dokument + zgłoszenia #6–#9 i #11 |
| C5 — przegląd | [`docs/reviews/uc-01.md`](../reviews/uc-01.md) + [#9](https://github.com/kollekka/Marabuty/issues/9) |
