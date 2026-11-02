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

## Uruchomienie

```bash
python -m pip install -r requirements.txt
python scripts/prepare_data.py data/raw/sample.csv data/processed/sample-clean.csv
```

Skrypt odrzuca duplikaty, rekordy bez ceny, w obcej walucie i z dużymi brakami, usuwa kolumny nieprzydatne w modelu, uzupełnia pozostałe braki i zapisuje dane gotowe do trenowania. Wynik dla próbki: `data/processed/sample-clean.csv` — 25 rekordów, 81 kolumn, 0 braków. Pełny eksport daje 228 318 rekordów i 81 kolumn.
