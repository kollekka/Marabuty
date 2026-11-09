# Model fizyczny — schemat plików

## Decyzja

MVP nie ma bazy danych. Zapis jest plikowy, zgodnie z [ADR-001](decisions/001-storage.md). Dlatego ten dokument **nie zawiera ERD bazy ani DDL** — logiczne powiązania opisuje [model logiczny](data-model.md), a poniżej znajduje się konkretny format plików, ścieżki i reguły zapisu.

Model fizyczny obejmuje:

- niezmienną migawkę źródłową,
- odtwarzalny plik przetworzony,
- artefakt modelu i manifest,
- wyniki analiz w wersjonowanych katalogach uruchomień.

## Struktura plików

```text
data/
  full-2026-11-01.csv              # niezmienna migawka źródłowa, 233 040 x 103
  raw/
    sample.csv                     # niezmienna próbka techniczna, 25 x 103
  processed/
    sample-clean.csv               # wynik prepare_data.py, 25 x 81
    full-2026-11-01.csv            # docelowy pełny wynik, 228 318 x 81 (zadanie #6)
models/
  price-ridge.joblib               # pipeline + interval_calibrator
  manifest.json                    # wersja modelu i danych, parametry, cechy
results/
  lab4/                            # istniejące wyniki Lab 4
    comparison.csv
    observations.csv
    sensitivity/
      comparison.csv
      observations.csv
  runs/                            # docelowy zapis nowych uruchomień
    <data_version>/
      <run_id>/
        run.json
        comparison.csv
        observations.csv
        forecast.csv                  # opcjonalny eksport pojedynczej wyceny
```

## `models/manifest.json`

Manifest jest odpowiednikiem `run.json` dla treningu modelu: wiąże artefakt z wersją danych i parametrami.

| Pole | Typ | Wymagane przez runtime | Reguła |
|---|---|---|---|
| `schema_version` | string | nie (proponowane) | Wersja kontraktu manifestu, np. `1.0`. |
| `model_version` | string | tak | Niepusty, unikalny identyfikator wersji modelu. |
| `data_version` | string | tak | Niepusty; wskazuje `DataSnapshot`, np. `otomoto-2026-11-01`. |
| `method` | string | tak | Niepusty, np. `ridge_log_linear`. |
| `target_transform` | string | tak | Dokładnie `log1p`. |
| `features` | array[string] | tak | Dokładnie kolejność `MODEL_FEATURES` z `app/runtime.py`. |
| `scope` | string | tak | Dokładnie `Używane`. |
| `interval_method` | string | tak | Niepusty; metoda kalibracji przedziału. |
| `interval_coverage` | number | tak | `0 < interval_coverage < 1`. |
| `trained_at` | string | nie (proponowane) | Data treningu w ISO 8601 UTC. |
| `training_rows` | integer | nie (proponowane) | Liczba wierszy treningowych, `> 0`. |
| `input_sha256` | string | nie (proponowane) | SHA256 pliku treningowego, 64 znaki hex. |
| `source_file` | string | nie (proponowane) | Ścieżka pliku migawki użytej do treningu. |
| `snapshot_date` | string | nie (proponowane) | Data migawki w ISO 8601. |
| `row_count` | integer | nie (proponowane) | Liczba wierszy migawki, `> 0`. |
| `column_count` | integer | nie (proponowane) | Liczba kolumn migawki, `> 0`. |
| `code_commit` | string | nie (proponowane) | Commit kodu treningu. |

Przykład:

```json
{
  "schema_version": "1.0",
  "model_version": "ridge-used-v1",
  "data_version": "otomoto-2026-11-01",
  "method": "ridge_log_linear",
  "target_transform": "log1p",
  "features": [
    "year",
    "mileage_km",
    "engine_cc",
    "engine_power_km",
    "make",
    "model",
    "fuel_type",
    "gearbox",
    "transmission",
    "body_type",
    "new_used",
    "region"
  ],
  "scope": "Używane",
  "interval_method": "residual_quantile",
  "interval_coverage": 0.9,
  "trained_at": "2026-11-09T12:00:00Z",
  "training_rows": 228318,
  "input_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
  "source_file": "data/full-2026-11-01.csv",
  "snapshot_date": "2026-11-01",
  "row_count": 233040,
  "column_count": 103,
  "code_commit": "0000000"
}
```

Uwagi:

- `schema_version`, `trained_at`, `training_rows`, `input_sha256`, `source_file`, `snapshot_date`, `row_count`, `column_count` i `code_commit` są metadanymi dodatkowymi; obecny `PredictionRuntime.from_files` ich nie wymaga. Walidacja tych pól w manifeście i plikach wynikowych należy do #11; runtime nie musi ich wymagać.
- Przykładowe `interval_method` i `interval_coverage` pokazują format, a nie wybraną metodę. Metoda i pokrycie przedziału są przedmiotem #4.

## `results/runs/<data_version>/<run_id>/run.json`

`run.json` opisuje jedno uruchomienie analizy. Jest niezbędny, żeby odbiorca wyników znał wersję danych, metody, parametry i datę uruchomienia.

| Pole | Typ | Reguła |
|---|---|---|
| `schema_version` | string | Wersja kontraktu, np. `1.0`. |
| `run_id` | string | Unikalny; format `YYYYMMDDTHHMMSSZ-<8 hex>` albo równoważny. |
| `data_version` | string | Wskazuje migawkę, np. `otomoto-2026-11-01`. |
| `method` | string | Metoda główna, np. `ridge_log_linear`. |
| `methods` | array[string] | Porównywane metody, np. `["baseline", "ridge"]`; niepusta lista. |
| `input_path` | string | Ścieżka względna do pliku wejściowego. |
| `input_sha256` | string | SHA256 pliku wejściowego, 64 znaki hex. |
| `test_size` | number | `0 < test_size < 1`. |
| `seed` | integer | `>= 0`; liczba całkowita. |
| `alpha` | number | `> 0`; parametr Ridge. |
| `code_commit` | string | Commit skryptu, który wykonał analizę. |
| `created_at` | string | Data uruchomienia w ISO 8601 UTC. |
| `outputs` | object | Ścieżki do `comparison.csv` i `observations.csv`; opcjonalnie `forecast` → `forecast.csv`. |
| `status` | string | `completed` albo `failed`. |

Przykład:

```json
{
  "schema_version": "1.0",
  "run_id": "20261109T120000Z-3f2a1c9d",
  "data_version": "otomoto-2026-11-01",
  "method": "ridge_log_linear",
  "methods": ["baseline", "ridge"],
  "input_path": "data/processed/sample-clean.csv",
  "input_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
  "test_size": 0.2,
  "seed": 42,
  "alpha": 1.0,
  "code_commit": "0000000",
  "created_at": "2026-11-09T12:00:00Z",
  "outputs": {
    "comparison": "comparison.csv",
    "observations": "observations.csv",
    "forecast": "forecast.csv"
  },
  "status": "completed"
}
```

Pole `outputs.forecast` jest opcjonalne; pojawia się tylko wtedy, gdy `forecast.csv` został wygenerowany.

## `comparison.csv`

Jeden wiersz to wynik jednej metody w jednym uruchomieniu. Klucz główny: `(split, method)`.

| Kolumna | Typ | Jednostka | Reguła |
|---|---|---|---|
| `split` | string | — | Etykieta podziału, np. `80_20`. |
| `test_size` | number | udział | `0 < test_size < 1`. |
| `seed` | integer | — | `>= 0`. |
| `method` | string | — | `baseline` albo `ridge`. |
| `n_train` | integer | wiersze | `> 0`. |
| `n_test` | integer | wiersze | `> 0`. |
| `mae_pln` | number | PLN | Skończone, `>= 0`. |
| `rmse_pln` | number | PLN | Skończone, `>= 0`. |
| `r2` | number | — | Skończone; może być ujemne. |
| `mape_pct` | number | % | Skończone, `>= 0`; tylko ceny `> 0`. |

## `observations.csv`

Jeden wiersz to jedna obserwacja testowa w jednym uruchomieniu. Klucz główny: `(split, row_index)`; `id` wskazuje `ProcessedListing.id`.

| Kolumna | Typ | Jednostka | Reguła |
|---|---|---|---|
| `split` | string | — | Etykieta podziału. |
| `row_index` | integer | — | Indeks wiersza w zbiorze wejściowym. |
| `id` | integer | — | FK do `ProcessedListing.id`. |
| `make`, `model` | string | — | Nazwy ze słownika danych. |
| `year` | integer | rok | `1950–2027` dla danych po filtrze. |
| `mileage_km` | integer | km | `0–2 000 000`. |
| `price_pln` | number | PLN | Rzeczywista cena ofertowa, `> 0`. |
| `baseline_pred_pln` | number | PLN | Prognoza baseline, `> 0`. |
| `model_pred_pln` | number | PLN | Prognoza Ridge, `> 0`. |
| `baseline_abs_error_pln` | number | PLN | `>= 0`. |
| `model_abs_error_pln` | number | PLN | `>= 0`. |
| `baseline_ape_pct` | number | % | `>= 0`. |
| `model_ape_pct` | number | % | `>= 0`. |

## `forecast.csv` (opcjonalny)

To opcjonalny eksport **pojedynczej wyceny**, a nie historia wycen ani prognoza szeregu czasowego. Powstaje tylko wtedy, gdy prowadzący lub odbiorca wymaga takiego pliku; nie jest częścią MVP. Jeden wiersz oznacza jedną wycenę.

| Kolumna | Typ | Jednostka | Reguła |
|---|---|---|---|
| `data` | string | — | Data wyceny w ISO 8601 UTC. |
| `wartosc` | number | PLN | Skończona, dodatnia prognoza. |
| `jednostka` | string | — | Dokładnie `PLN`. |
| `model_version` | string | — | Opcjonalna wersja modelu. |
| `data_version` | string | — | Opcjonalna wersja danych. |

Plik trafia do katalogu `results/runs/<data_version>/<run_id>/` i podlega tej samej zasadzie braku nadpisań co pozostałe wyniki. Nie jest historią wycen ani serią czasową; podstawowymi wynikami pozostają `comparison.csv` i `observations.csv`.

## `data/processed/sample-clean.csv`

- 25 wierszy × 81 kolumn; wynik `scripts/prepare_data.py` z `data/raw/sample.csv`.
- Klucz: `id`, unikalny.
- Brak braków w komórkach.
- Typy i jednostki zgodne ze [słownikiem danych](data-dictionary.md): `year`, `mileage_km`, `price_pln`, `engine_cc`, `engine_power_km` jako liczby całkowite; flagi `0/1`; `created_at` w formacie `YYYY-MM-DDTHH:MM:SSZ`.
- Zakresy po czyszczeniu: `price_pln >= 1000`, `mileage_km <= 2 000 000`, `year` w `1950–2027`, `engine_cc` w `500–8000`, `engine_power_km` w `20–2000`.
- Plik nie zawiera pól pochodnych ani nowych wskaźników.

## Zasada unikania nadpisań

1. **Migawka źródłowa jest niezmienna.** `data/full-2026-11-01.csv` ma w nazwie datę migawki. Nowe pobranie dostaje nową nazwę i nowy `data_version`; nie nadpisuje starego pliku.
2. **Plik przetworzony jest odtwarzalny.** Dla tej samej migawki i tej samej wersji skryptu wynik powinien mieć identyczny SHA256. Nowa wersja danych dostaje nową nazwę, np. `full-2026-12-01.csv`; nie nadpisuje `full-2026-11-01.csv`.
3. **Wersja modelu jest niezmienna.** `model_version` w manifeście identyfikuje artefakt. Nowy model dostaje nowy `model_version`; aktywny zestaw w `models/` jest podmieniany atomowo, a poprzedni trafia do archiwum `models/archive/<model_version>/`.
4. **Wyniki trafiają do unikalnego katalogu runu.** Nowy format to `results/runs/<data_version>/<run_id>/` z `run.json`, `comparison.csv`, `observations.csv` i opcjonalnym `forecast.csv`. Jeśli katalog `run_id` już istnieje, skrypt kończy się błędem i nie nadpisuje plików. `run_id` zawiera czas i skrót parametrów, np. `20261109T120000Z-3f2a1c9d`.
5. **Zapis jest atomowy.** Pliki powstają jako `*.tmp`, a po poprawnym zapisie są przenoszone przez `os.replace`. Nie zapisujemy bezpośrednio do pliku docelowego.
6. **Metadane wiążą wynik z wejściem.** `run.json` zawiera `input_sha256`, `data_version`, `method`, `methods`, `code_commit` i `created_at`; manifest zawiera `model_version`, `data_version` i `input_sha256`.
7. **Stan obecny.** `results/lab4/` jest stałym katalogiem z Lab 4 i nie ma `run.json`; ponowne uruchomienie z tym samym `--output-dir` nadpisuje `comparison.csv` i `observations.csv`. To luka opisana w #8; nowe uruchomienia powinny korzystać z `results/runs/`.

## Walidacja, której nie da się wymusić w CSV/JSON

Pliki CSV i JSON nie mają kluczy obcych, transakcji ani typów wymuszanych przez silnik bazy. Dlatego aplikacja i skrypty muszą sprawdzać:

- poprawną datę kalendarzową w `created_at`, `snapshot_date`, `trained_at` i `created_at` runu — sam format ISO 8601 nie wystarcza,
- skończoność liczb (`math.isfinite`) — `inf` i `NaN` nie mogą trafić do prognozy ani metryk,
- całkowitość `seed` i dodatniość `test_size`, `alpha` oraz `interval_coverage`,
- zgodność `data_version` między manifestem, runem i migawką,
- dokładną kolejność `features` w manifeście względem `MODEL_FEATURES`,
- unikalność `id` w `Listing`/`ProcessedListing`, `(split, method)` w `comparison.csv` i `(split, row_index)` w `observations.csv`,
- relację `observations.id` → `ProcessedListing.id`,
- zakresy i flagi `0/1` w danych przetworzonych,
- `lower_pln <= estimated_price_pln <= upper_pln` w odpowiedzi API,
- poprawność opcjonalnego `forecast.csv`: data ISO 8601, `wartosc` skończona i dodatnia, `jednostka = PLN`,
- brak braków w pliku przetworzonym i wynikach.

Istniejące kontrole: `scripts/prepare_data.py` (czyszczenie i zakresy), `scripts/quality_checks.py` (10 kontroli pliku przetworzonego), `scripts/compare_methods.py` (wymagane kolumny, braki, ceny dodatnie) oraz `app/schemas.py` i `app/runtime.py` (walidacja żądania i wyniku). Luki: brak walidacji manifestu, `run.json`, opcjonalnego `forecast.csv`, unikalności kluczy wyników i skończoności liczb w CSV — zadanie #11.

## Mapowanie wymagań C2 na pliki

| Wymóg C2 | Plik | Status |
|---|---|---|
| wersja danych, metoda, parametry | `run.json` | wymagany dla nowego runu |
| data, wartość, jednostka | `forecast.csv` | opcjonalny eksport pojedynczej wyceny |
| metryki porównywanych metod | `comparison.csv` | podstawowy wynik runu porównawczego |
| predykcje dla wierszy testowych | `observations.csv` | podstawowy wynik runu porównawczego |

UC-01 nie jest prognozą szeregu czasowego: dotyczy jednego samochodu i jednej migawki. Dlatego `forecast.csv` nie jest serią `data → wartość` ani historią wycen. Jeśli prowadzący wymaga tego pliku, używamy kolumn `data`, `wartosc`, `jednostka`; jeśli nie — wystarczą `comparison.csv` i `observations.csv`.
