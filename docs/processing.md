# Przetwarzanie danych

## Dobór narzędzi

| Element | Wybór |
|---|---|
| Źródło i format danych | `data/raw/sample.csv` — eksport ogłoszeń Otomoto w CSV UTF-8 z BOM: 25 rekordów i 103 kolumny. Pełny eksport `data/full-2026-11-01.csv` zawiera 233 040 rekordów i 103 kolumny. |
| Narzędzie główne | Python 3.9.13 i pandas 2.3.3; skrypt `scripts/prepare_data.py`. |
| Dlaczego pasuje | pandas obsługuje CSV, braki, typy i przekształcenia tabelaryczne, a skrypt jest powtarzalny i nie wymaga bazy danych ani usług zewnętrznych. |
| Narzędzie pomocnicze | `scripts/quality_checks.py` do automatycznych kontroli PASS/FAIL oraz katalog `data/test/` na kopie błędne i test powtarzalności. |
| Wynik zapisany w repozytorium | `data/processed/sample-clean.csv` — 25 rekordów, 81 kolumn, 0 braków w komórkach; logi uruchomień w `data/test/`. |

## Kroki przetwarzania

| Krok | Operacja | Powód | Wpływ na dane |
|---|---|---|---|
| 1 | Wczytanie `data/raw/sample.csv` | Odczyt źródła w formacie CSV UTF-8 z BOM. | 25 rekordów i 103 kolumny na wejściu. |
| 2 | Usunięcie duplikatów `id` | Jeden wiersz ma odpowiadać jednemu ogłoszeniu. | Usunięto 0 rekordów. |
| 3 | Odrzucenie walut innych niż PLN | W danych nie ma kursu wymiany pozwalającego porównać ceny. | Usunięto 0 rekordów. |
| 4 | Odrzucenie rekordów bez `price_pln` | Brak zmiennej objaśnianej uniemożliwia uczenie modelu. | Usunięto 0 rekordów. |
| 5 | Odrzucenie rekordów z ponad 50% braków w 17 polach rdzeniowych | Zbyt niepełny rekord nie daje wiarygodnej wyceny. | Usunięto 0 rekordów. |
| 6 | Odrzucenie wartości niemożliwych | Cena poniżej 1000 PLN, przebieg powyżej 2 000 000 km, rok poza 1950–2026, pojemność poza 500–8000 cm³ i moc poza 20–2000 KM. | Usunięto 0 rekordów w każdej kontroli. |
| 7 | Usunięcie 22 kolumn | Identyfikatory i dane sprzedawcy, metadane scrapera, kolumny puste, o wysokich brakach lub będące kopią innej kolumny. | Liczba kolumn spadła z 103 do 81. |
| 8 | Normalizacja tekstu, typów i daty `created_at` | Spójne typy i format daty ułatwiają modelowanie i kontrole jakości. | `created_at` zapisano jako `YYYY-MM-DDTHH:MM:SSZ`. |
| 9 | Uzupełnienie braków | Mediana dla liczb, etykieta `Nieznana` dla kategorii i 0 dla flag. | Braki w komórkach spadły z 283 do 0. |
| 10 | Zapis wyniku | Wynik ma być gotowy do trenowania i kontroli. | Zapisano `data/processed/sample-clean.csv`: 25 rekordów, 81 kolumn. |

Uzupełnione braki w próbce: `seats` 1 (mediana), `transmission` 4, `generation` 6, `color_type` 10, `country_origin` 8, `ac_type` 3, `cruise_type` 10, `alloy_wheels_type` 6, `headlights_type` 15, `drive_type` 4 (etykieta `Nieznana`) oraz flagi `has_*` i pola stanu, m.in. `has_sunroof` 21, `has_led_lights` 15, `first_owner` 13, `registered_pl` 11, `service_aso` 9, `no_accident` 7, `has_leather` 5, `damaged` 5, `imported` 3 (wartość 0).

## Kontrole jakości

| Kontrola | Wynik | Działanie lub ograniczenie |
|---|---|---|
| Rekordy | 25 → 25, usunięto 0 | Próbka nie zawiera duplikatów, braków ceny ani wartości niemożliwych. Większy zbiór może wymagać odrzuceń. |
| Braki | 283 → 0 | Uzupełniono medianą, etykietą `Nieznana` i zerami. Imputacja może zniekształcać rozkłady. |
| Duplikaty | 0 duplikatów `id`, kontrola PASS | Klucz `id` jest unikalny w próbce. `prepare_data.py` usuwa duplikaty przed dalszym przetwarzaniem. |
| Zakresy i jednostki | Wszystkie wartości w zakresie, kontrola PASS | Cena w PLN, przebieg w km, pojemność w cm³, moc w KM. Dostępne są ceny ofertowe, nie transakcyjne. |
| Typy i format daty | Wszystkie kolumny liczbowe, data w ISO 8601, kontrola PASS | Kontrola typów nie zastępuje oceny merytorycznej wartości. |
| Flagi 0/1 | 51 kolumn flag poprawnych | 0 oznacza „nie zadeklarowano w ogłoszeniu”, a nie „auto nie ma cechy”. |
| Kategorie | Kategorie `new_used` i `gearbox` dozwolone | Kontrola obejmuje tylko jawnie zdefiniowane listy wartości. |
| Kompletność kluczy | Brak braków w `id`, `created_at` i `price_pln` | Kontrola dotyczy wyłącznie kolumn kluczowych, nie całego zbioru. |
| Powtarzalność | Identyczny SHA256, 25 rekordów i 81 kolumn, identyczne wartości | Wynik jest odtwarzalny na tym samym pliku wejściowym i wersji pandas. |

Kontrola błędnej kopii `data/test/sample-bad.csv` dała 7 PASS i 3 FAIL oraz kod wyjścia 1. Wykryto zduplikowane ID, cenę 500 PLN poza zakresem i datę `2026-13-40T99:99:99Z`. Oczekiwany wynik opisuje `data/test/quality_checks-expected.txt`, a uzyskany `data/test/quality_checks-bad.log`.

## Test powtarzalności

Kopię wyniku zapisano jako `data/test/sample-clean-before-repro.csv`, następnie usunięto `data/processed/sample-clean.csv` i odtworzono go poleceniem z README. Porównanie objęło liczbę rekordów, nazwy i kolejność kolumn, typy oraz wartości.

| Element | Przed odtworzeniem | Po odtworzeniu |
|---|---|---|
| SHA256 pliku | `E587E282D0A2F5D449F0330338033C9D074216A22718CF4199F0F5DA0D189A5B` | `E587E282D0A2F5D449F0330338033C9D074216A22718CF4199F0F5DA0D189A5B` |
| Rekordy | 25 | 25 |
| Kolumny | 81 | 81 |
| Identyczny kształt | — | tak |
| Identyczne nazwy i kolejność kolumn | — | tak |
| Identyczne typy kolumn | — | tak |
| Identyczne wartości | — | tak |

Logi testu: `data/test/prepare_data-repro.log`, `data/test/reproducibility-compare.log` i `data/test/quality_checks-repro.log`.

## Uruchomienie i wyniki

```bash
python -m pip install -r requirements.txt
python scripts/prepare_data.py data/raw/sample.csv data/processed/sample-clean.csv
python scripts/quality_checks.py data/processed/sample-clean.csv
```

Fragment logu przetwarzania:

```text
Plik wejściowy:  data\raw\sample.csv
Plik wyjściowy:  data\processed\sample-clean.csv

Rekordy:  25 -> 25  (usunięto 0)
Kolumny:  103 -> 81  (usunięto 22)

Braki w komórkach: 283 -> 0
Zapisano 25 rekordów i 81 kolumn.
```

Kontrola jakości zakończyła się wynikiem:

```text
Kontrole: 10 PASS, 0 FAIL
Wynik: PASS
```

Kod wyjścia kontroli: 0.

## Ograniczenia

- Brak cen transakcyjnych uniemożliwia potwierdzenie, że prognoza odpowiada rzeczywistej cenie sprzedaży.
- Jedna migawka danych uniemożliwia ocenę zmian cen w czasie i aktualności modelu.
- Brak flagi wyposażenia nie pozwala rozstrzygnąć, czy auto nie ma cechy, czy sprzedawca jej nie zadeklarował. Przyjęte 0 jest założeniem.
- Imputacja medianą i etykietą `Nieznana` nie odtwarza rzeczywistych wartości i może zniekształcać rozkłady cech.
- Decyzja o przeliczeniu cen w EUR jest niemożliwa bez kursu wymiany i daty przewalutowania, dlatego `prepare_data.py` odrzuca ogłoszenia w walutach innych niż PLN.
- Próbka 25 rekordów służy do testów technicznych, a nie do wnioskowania o całym rynku.
