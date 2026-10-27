# Przetwarzanie danych

Dokument opisuje przygotowanie próbki `data/raw/sample.csv` do pliku `data/processed/sample-clean.csv`, kontrole jakości oraz test powtarzalności. Wyniki pochodzą z uruchomień opisanych niżej; danych w `data/raw/` nie modyfikowano.

## Dobór narzędzi

### Źródło i format danych

- `data/raw/sample.csv`: CSV, 25 rekordów i 25 kolumn, separator przecinek, odczyt z kodowaniem `utf-8-sig`.
- Jest to techniczna próbka pierwszych 25 rekordów, a nie próba losowa ani reprezentatywna.
- Pełny zbiór `data/Car_sale_ads.csv` ma 208 304 rekordy (zgodnie z `docs/data.md`).

### Narzędzie główne

Python z biblioteką pandas. Środowisko testowe: Python 3.13, pandas 2.3.3, numpy 2.0.2. Plik `requirements.txt` deklaruje `pandas>=2.0` i `numpy>=1.22`, a README wskazuje Python 3.10 lub nowszy.

### Dlaczego pasuje

pandas obsługuje odczyt i zapis CSV, usuwanie duplikatów, konwersję dat i liczb oraz dodawanie kolumn pochodnych. Dzięki temu całe przygotowanie danych jest jednym, powtarzalnym skryptem, a wynik można zapisać w ustalonym formacie.

### Narzędzie pomocnicze

- `scripts/quality_checks.py` — osiem kontroli jakości CSV z wynikiem `PASS`/`FAIL` i kodem wyjścia `1` przy naruszeniu.
- SHA256 (`Get-FileHash` w PowerShell) — porównanie plików w teście powtarzalności.

### Wynik zapisany w repozytorium

- `data/processed/sample-clean.csv` — oczyszczona próbka: 25 rekordów i 27 kolumn.
- `docs/data-dictionary.md` — słownik danych źródłowych i wynikowych.
- `data/test/` — błędna kopia, logi kontroli i materiał do testu powtarzalności.

## Kroki przetwarzania

| Krok | Operacja | Powód | Wpływ na dane |
|---|---|---|---|
| 1 | Odczyt CSV z `utf-8-sig` i `low_memory=False`. | Poprawny odczyt polskich znaków i obsługa większego pliku. | Powstała ramka 25 rekordów × 25 kolumn; plik wejściowy pozostał bez zmian. |
| 2 | Usunięcie zbędnych białych znaków z pól tekstowych. | Spójność wartości tekstowych i kategorii. | Wartości tekstowe są przycinane; liczba rekordów się nie zmienia. |
| 3 | Usunięcie duplikatów po wszystkich kolumnach poza `Index`. | `Index` jest technicznym identyfikatorem i uniemożliwiłby wykrycie powtórzeń. | Usunięto 0 duplikatów; liczba rekordów pozostała 25. |
| 4 | Ujednolicenie dat do `YYYY-MM-DD`; błędne daty stają się brakami. | Spójny format dat do dalszej analizy. | Daty `DD/MM/YYYY` zamieniono na ISO. Braki: `First_registration_date` 17 → 17, `Offer_publication_date` 0 → 0. |
| 5 | Konwersja kolumn liczbowych; wartości niemożliwe stają się brakami. | Poprawne typy liczbowe i odporne reguły jakości. | W próbce 0 wartości oznaczono jako niemożliwe; liczby braków w kolumnach źródłowych nie wzrosły. |
| 6 | Dodanie `Displacement_l` i `Vehicle_age`. | Przeliczenie pojemności na litry i obliczenie wieku pojazdu. | Liczba kolumn wzrosła z 25 do 27. `Displacement_l = Displacement_cm3 / 1000`; `Vehicle_age` to różnica roku publikacji i roku produkcji. Rok odniesienia: 2021. |
| 7 | Zapis `data/processed/sample-clean.csv` w UTF-8, bez indeksu. | Powtarzalny wynik w repozytorium. | Zapisano 25 rekordów i 27 kolumn; `data/raw/sample.csv` nie został zmieniony. |

## Podsumowanie kontroli

| Kontrola | Wynik | Działanie lub ograniczenie |
|---|---|---|
| Rekordy | 25 przed i 25 po; 27 kolumn po przetworzeniu. | Wynik zgodny z README; wiersze nie są usuwane poza uzasadnionymi duplikatami. |
| Braki | 7 kolumn z brakami: `Vehicle_version` 24, `Vehicle_generation` 25, `CO2_emissions` 20, `Drive` 3, `Origin_country` 13, `First_owner` 18, `First_registration_date` 17. Liczby przed i po są takie same. | Braki pozostają w danych; model musi je obsłużyć. Nie usuwamy wierszy z powodu pojedynczych braków. |
| Duplikaty | W próbce usunięto 0 duplikatów; kontrola wykazała 0 duplikatów. | Duplikaty są usuwane po wszystkich kolumnach poza `Index`. Interpretacja duplikatów w pełnym zbiorze wymaga EDA. |
| Zakresy i jednostki | 0 wartości niemożliwych oznaczonych jako braki; kontrola zakresów: PASS. `Price` w PLN, `Mileage_km` w km, `Power_HP` w HP, `Displacement_cm3` w cm³, `Displacement_l` w litrach. | Reguły: `Price > 0`, `Mileage_km >= 0`, `Power_HP > 0`, `Displacement_cm3 > 0`, `Doors_number > 0`, `CO2_emissions >= 0`, `Production_year` w zakresie 1900–2022. Jednostka `CO2_emissions` wymaga potwierdzenia. |
| Typy, kategorie i daty | Kontrola na oczyszczonym pliku: `PASS (8/8)`, kod `0`. | Wszystkie 27 kolumn przeszło kontrolę typów logicznych; kategorie mieszczą się w listach dozwolonych; brak błędnych dat. |
| Test błędnej kopii | `FAIL (5/8)`, kod `1`. | Wykryto powtórzone ID (2 wiersze), ujemną wartość `Mileage_km` i nieznaną kategorię `Condition = Damaged`. Oczekiwany i uzyskany log są w `data/test/`. |
| Powtarzalność | SHA256 pliku przed i po ponownym przetworzeniu jest identyczny. | Wynik odtwarzalny przy tym samym skrypcie i środowisku. |

## Test powtarzalności

1. Skopiowano wynik do `data/test/sample-clean-before-repro.csv`.
2. Usunięto `data/processed/sample-clean.csv`.
3. Uruchomiono zgodnie z README:

   ```bash
   python scripts/prepare_data.py data/raw/sample.csv data/processed/sample-clean.csv
   ```

4. Odtworzony plik ma 25 rekordów i 27 kolumn.
5. SHA256 przed: `BE5ACCF1C82EDC296B2FB0B49DFD6046F796CDDBE8DBAA5C51BD634647E9F907`.
6. SHA256 po: `BE5ACCF1C82EDC296B2FB0B49DFD6046F796CDDBE8DBAA5C51BD634647E9F907`.
7. Hashe są identyczne, więc struktura i wartości są takie same.
8. SHA256 `data/raw/sample.csv` przed i po: `B49582AAD7354EC18679000887C5D7FBFD073F1F1612A93253240C0A02CD02AB`; plik surowy nie został zmieniony.
9. Kontrola jakości odtworzonego pliku: `PASS (8/8)`, kod `0`.

Logi: `data/test/prepare-data-repro.log`, `data/test/quality-check-repro.txt` oraz `data/test/reproducibility-check.txt`.

## Ograniczenia

- Dostępne są ceny ofertowe, a nie transakcyjne; nie można na tej podstawie wyznaczyć rzeczywistej ceny transakcyjnej.
- Dane są migawką z jednego okresu; nie można na ich podstawie prognozować zmian cen w czasie.
- Braki w `Vehicle_version`, `Vehicle_generation`, `CO2_emissions`, `Drive`, `Origin_country`, `First_owner` i `First_registration_date` uniemożliwiają wykorzystanie tych pól bez decyzji o imputacji lub odrzuceniu; decyzja wymaga EDA.
- Nie można rozstrzygnąć, czy powtórzone wiersze w pełnym zbiorze są błędami duplikacji, czy osobnymi ogłoszeniami, bez dokumentacji źródła i analizy ogłoszeń.
- Próbka 25 rekordów nie jest reprezentatywna, więc nie należy na jej podstawie uogólniać rozkładów na cały zbiór.
