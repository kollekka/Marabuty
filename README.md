# Prognozowanie cen używanych samochodów osobowych

Projekt zespołu **Marabuty**: model regresyjny i narzędzie do orientacyjnej wyceny samochodów używanych na polskim rynku ogłoszeń.

## Problem

Cena samochodu używanego zależy jednocześnie od wielu cech, a ogłoszenia podobnych aut różnią się na tyle mocno, że kupujący i sprzedający nie mają prostego punktu odniesienia. Projekt sprawdza, jak dokładnie można przewidzieć cenę ofertową na podstawie parametrów pojazdu i które cechy wpływają na nią najsilniej.

## Zespół

- Kacper Stopa
- Adrian Świeca
- Bartłomiej Taper

## Dokumentacja

- [Opis problemu](docs/problem.md)
- [Ocena źródła danych](docs/data.md)
- [Słownik danych](docs/data-dictionary.md)
- [Próbka danych (25 rekordów)](data/raw/sample.csv)

## Dane

Głównym źródłem są publiczne ogłoszenia z Otomoto.pl pozyskane własnym eksportem opartym na skrypcie [`MrKabas/Otomoto-Scraper`](https://github.com/MrKabas/Otomoto-Scraper) (MIT, autor: Kacper Stopa z zespołu Marabuty). Pełny eksport `data/full-2026-11-01.csv` zawiera 233 040 rekordów i 103 kolumny; `data/raw/sample.csv` to losowa próbka 25 rekordów (ziarno 42). Szczegóły, braki i ograniczenia opisuje [docs/data.md](docs/data.md).

## Środowisko i uruchomienie

Wymagany jest Python 3.9 lub nowszy (projekt testowano na 3.9.13). Zależności są zapisane w `requirements.txt` (`pandas>=2.0`, `scikit-learn>=1.3`).

```bash
python -m pip install -r requirements.txt
python scripts/prepare_data.py data/raw/sample.csv data/processed/sample-clean.csv
python scripts/quality_checks.py data/processed/sample-clean.csv
```

Na Windows, jeśli polecenie `python` nie jest dostępne w PATH, tych samych poleceń można użyć przez `py`.

Przetwarzanie próbki daje `data/processed/sample-clean.csv` z 25 rekordami i 81 kolumnami, bez braków w komórkach. Pełny eksport daje 228 318 rekordów i 81 kolumn. Kontrola jakości wypisuje `PASS` lub `FAIL` dla każdej kontroli i kończy się `Wynik: PASS` oraz kodem 0; dla próbki przechodzi 10 z 10 kontroli. Kod różny od zera oznacza naruszenie i wypisanie `FAIL`.

## Lab 4: uruchomienie porównania

Porównanie baseline (mediana ceny dla marki i modelu) z regresją Ridge opisuje [docs/experiment.md](docs/experiment.md). Skrypt to `scripts/compare_methods.py`.

### Środowisko `.venv`

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Linux i macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Katalog `.venv` nie trafia do repozytorium.

### Wyniki podstawowe (80/20)

```bash
python scripts/compare_methods.py data/processed/sample-clean.csv --output-dir results/lab4 --test-size 0.2 --seed 42
```

### Próba wrażliwości (70/30)

```bash
python scripts/compare_methods.py data/processed/sample-clean.csv --output-dir results/lab4/sensitivity --test-size 0.3 --seed 42
```

Zmienia się wyłącznie `--test-size`. Ziarno 42 i `alpha=1.0` pozostają bez zmian, a wyniki wrażliwości trafiają do osobnego katalogu i nie nadpisują wyników podstawowych.

### Pliki wynikowe

| Plik | Zawartość |
|---|---|
| `results/lab4/comparison.csv` | 2 wiersze — baseline i ridge dla podziału 80/20; kolumny `split`, `test_size`, `seed`, `method`, `n_train`, `n_test`, `mae_pln`, `rmse_pln`, `r2`, `mape_pct` |
| `results/lab4/observations.csv` | 5 wierszy testowych — rzeczywista cena, prognozy obu metod, błędy bezwzględne i APE |
| `results/lab4/sensitivity/comparison.csv` | te same kolumny dla podziału 70/30 (17/8) |
| `results/lab4/sensitivity/observations.csv` | 8 wierszy testowych dla podziału 70/30 |

Skrypt sprawdza wejście (wymagane kolumny, brak braków, ceny dodatnie), blokuje nadpisanie pliku wejściowego i wypisuje wzory metryk wraz z ręcznym przykładem na trzech liczbach.
