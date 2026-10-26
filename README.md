# Prognozowanie cen używanych samochodów

Projekt zespołu Marabuty: model regresyjny i narzędzie do szacowania cen samochodów używanych na polskim rynku ogłoszeń.

## Problem

Ceny podobnych samochodów różnią się, a kupujący i sprzedający często muszą porównywać ogłoszenia ręcznie. Projekt sprawdza, czy cenę ofertową można przewidywać na podstawie parametrów pojazdu i które cechy mają na nią największy wpływ.

## Zespół

- Kacper Stopa 
- Adrian Świeca
- Bartłomiej Taper 

## Dokumentacja

- [Opis problemu](docs/problem.md)
- [Ocena danych i źródła](docs/data.md)
- [Próbka danych (25 rekordów)](data/raw/sample.csv)

## Środowisko i uruchomienie

- **Wymagany Python:** 3.10 lub nowszy (projekt testowany na Pythonie 3.10).
- **Instalacja zależności:**

  ```bash
  python -m pip install -r requirements.txt
  ```

- **Przetwarzanie danych:**

  ```bash
  python scripts/prepare_data.py data/raw/sample.csv data/processed/sample-clean.csv
  ```

  Skrypt wypisuje liczbę rekordów przed i po, liczbę usuniętych duplikatów oraz liczbę braków, a wynik zapisuje w `data/processed/sample-clean.csv` (katalog tworzony automatycznie). Skrypt odmawia zapisu, gdy ścieżka wyjściowa jest taka sama jak wejściowa.

- **Kontrola jakości:**

  ```bash
  python scripts/quality_checks.py data/processed/sample-clean.csv
  ```

  Skrypt wypisuje liczbę rekordów i kolumn, liczbę duplikatów oraz braki w oczyszczonym zbiorze.

- **Oczekiwane wyniki dla próbki:** wejście `data/raw/sample.csv` ma 25 rekordów; po przetworzeniu `data/processed/sample-clean.csv` ma 25 rekordów, 27 kolumn (dodane `Displacement_l` i `Vehicle_age`) i 0 duplikatów.
