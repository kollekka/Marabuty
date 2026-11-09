# ADR-001: Plikowy artefakt modelu bez historii prognoz

**Status:** przyjęta dla MVP

## Kontekst

Docelowy system jest aplikacją webową z formularzem React i API FastAPI. Model jest trenowany offline na migawce ogłoszeń, a podczas żądania API system oblicza wycenę jednego samochodu. Wymagania R1–R3 opisują wynik prognozy i ocenę ceny oferty, ale nie wymagają kont użytkowników, wspólnej historii wycen, filtrowania wcześniejszych wyników ani równoczesnego zapisu wielu prognoz.

W repozytorium działają już skrypty przetwarzające i ewaluujące pliki CSV. `scripts/compare_methods.py` zapisuje wyniki ewaluacji, ale nie zapisuje wytrenowanego modelu do późniejszej predykcji. Artefakt dla aplikacji będzie więc nowym rezultatem treningu offline.

## Decyzja

- Wytrenowany pipeline modelu i jego metadane przechowujemy jako pliki: `models/price-ridge.joblib` oraz `models/manifest.json`.
- Manifest identyfikuje model i dane treningowe oraz zawiera zakres `Używane`, target, listę i typy cech, transformację celu, parametry Ridge oraz metodę i poziom pokrycia przedziału niepewności.
- FastAPI wczytuje i weryfikuje zestaw plików przy uruchomieniu. Brak artefaktu, kalibratora lub zgodności schematu oznacza brak gotowości usługi; API zwraca `503 model_not_ready` i nie udaje prognozy.
- Pojedyncze żądania i odpowiedzi prognozy nie są trwale zapisywane w MVP. Wynik wraca do klienta jako JSON. CSV z `results/lab4/` pozostają artefaktami ewaluacji, a nie historią użytkowników.
- Model musi być wytrenowany i oceniony na pełnym zbiorze aut `Używane`; próbka 25 rekordów jest wyłącznie techniczna.

## Rozważane alternatywy

| Alternatywa | Powód odrzucenia na MVP |
|---|---|
| SQLite/PostgreSQL dla prognoz i historii uruchomień | Nie ma wymagania odczytu historii, współdzielenia wyników ani współbieżnego zapisu. Baza dodałaby migracje, klucze, transakcje i obsługę blokad bez obecnej korzyści użytkowej. |
| Trenowanie modelu przy każdym żądaniu | Zwiększa opóźnienie, powtarza koszt obliczeń i utrudnia stabilne przypisanie wyniku do wersji modelu oraz danych. |
| Zapis każdej prognozy do pliku | Nie jest potrzebny do R1/R3 i gromadziłby parametry aut oraz ceny ofertowe bez funkcji przeglądu historii. |

## Konsekwencje

- Każdy wynik identyfikuje wersję modelu i danych, a API używa jednego zgodnego zestawu artefaktu i manifestu.
- Aktualizacja modelu polega na przygotowaniu i walidacji nowej wersji artefaktu, a nie na zmianie rekordu w bazie.
- Użytkownik nie może przeglądać wcześniejszych wycen ani porównywać ich w czasie.
- Pliki wyników Lab 4 nie mogą być użyte jako model do predykcji: zawierają metryki i przykłady testowe, nie zapisany pipeline.

## Warunek ponownego rozważenia

Wrócić do decyzji o bazie danych, jeśli pojawi się wymaganie historii wycen, kont użytkowników, wspólnego dostępu, raportowania po wielu żądaniach albo audytowalnego rejestru prognoz.
