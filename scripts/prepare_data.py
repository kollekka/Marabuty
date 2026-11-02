#!/usr/bin/env python3
"""Przygotowanie eksportu Otomoto do trenowania modelu.

Skrypt wykonuje realne czyszczenie danych, a nie tworzenie sztucznych cech:

1. usuwa duplikaty ogłoszeń (klucz ``id``),
2. odrzuca wiersze bez zmiennej objaśnianej (``price_pln``) i w obcej walucie,
3. odrzuca wiersze z dużymi brakami oraz wartościami niemożliwymi,
4. usuwa kolumny puste, stałe, identyfikujące sprzedawcę lub będące
   kopią innej kolumny,
5. uzupełnia pozostałe braki: medianą (liczby), etykietą ``Nieznana``
   (kategorie) i zerem (flagi 0/1),
6. ujednolica typy i format dat.

Uruchomienie::

    python scripts/prepare_data.py data/raw/sample.csv data/processed/sample-clean.csv
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Pola, których brak w więcej niż połowie wierszy dyskwalifikuje rekord.
CORE_FIELDS = [
    "make",
    "model",
    "year",
    "mileage_km",
    "price_pln",
    "fuel_type",
    "gearbox",
    "transmission",
    "engine_cc",
    "engine_power_km",
    "body_type",
    "door_count",
    "seats",
    "color",
    "new_used",
    "city",
    "region",
]
MAX_CORE_MISSING_SHARE = 0.5

# Kolumny usuwane zawsze, z uzasadnieniem. Klucz: nazwa kolumny, wartość: powód.
DROP_COLUMNS = {
    # Identyfikatory i dane sprzedawcy - nie są cechami pojazdu.
    "url": "adres ogłoszenia, unikalny dla wiersza",
    "title": "tekst ogłoszenia, duplikuje make i model",
    "seller_id": "identyfikator sprzedawcy",
    "seller_name": "nazwa sprzedawcy",
    # Metadane scrapera, nie opisują pojazdu.
    "updated_at": "data aktualizacji rekordu w bazie scrapera",
    "first_seen": "znacznik uruchomienia scrapera, stały w całym eksporcie",
    "last_seen": "znacznik uruchomienia scrapera, stały w całym eksporcie",
    "enriched_at": "data uzupełnienia szczegółów przez scraper",
    "state": "stan przetwarzania rekordu przez scraper",
    "attempts": "liczba prób pobrania szczegółów",
    "status": "status ogłoszenia w bazie scrapera",
    # Po odfiltrowaniu walut innych niż PLN kolumna jest stała.
    "currency": "po filtrze zawiera wyłącznie PLN",
    # Całkowicie puste w eksporcie - API zwraca te pola zaszyfrowane.
    "vin": "100% braków w danych źródłowych",
    "first_registration": "100% braków w danych źródłowych",
    "last_error": "100% braków w danych źródłowych",
    # Zbyt duży odsetek braków, żeby uzupełnianie miało sens.
    "district": "ponad 70% braków po odrzuceniu wierszy",
    # Dokładne kopie innych kolumn po uzupełnieniu braków zerem.
    "has_imported": "kopia kolumny imported",
    "is_damaged": "kopia kolumny damaged",
    "is_original_owner": "kopia kolumny first_owner",
    "is_no_accident": "kopia kolumny no_accident",
    "has_service_record": "kopia kolumny service_aso",
    "has_4wd": "kopia informacji zawartej w kolumnie transmission",
}

DATE_COLUMNS = ["created_at"]

NUMERIC_COLUMNS = [
    "year",
    "mileage_km",
    "price_pln",
    "engine_cc",
    "engine_power_km",
    "door_count",
    "seats",
    "photo_count",
    "airbags_count",
]

# Kolumny liczbowe uzupełniane medianą.
MEDIAN_FILL = [
    "engine_cc",
    "engine_power_km",
    "door_count",
    "seats",
    "photo_count",
    "airbags_count",
]

# Kolumny kategoryczne uzupełniane jawną etykietą braku.
CATEGORICAL_FILL = [
    "gearbox",
    "transmission",
    "generation",
    "color_type",
    "country_origin",
    "ac_type",
    "cruise_type",
    "alloy_wheels_type",
    "headlights_type",
    "drive_type",
    "seller_type",
]
UNKNOWN_LABEL = "Nieznana"

# Flagi 0/1. W danych źródłowych 0 znaczy "nie zadeklarowano w ogłoszeniu".
# Do listy dochodzą wszystkie kolumny rozpoczynające się od "has_".
BASE_FLAG_COLUMNS = [
    "damaged",
    "registered_pl",
    "first_owner",
    "no_accident",
    "service_aso",
    "imported",
]


def flag_columns(df: pd.DataFrame) -> list[str]:
    """Kolumny flag 0/1: stała lista plus wszystkie pola ``has_*``."""
    has_columns = [column for column in df.columns if column.startswith("has_")]
    return has_columns + [column for column in BASE_FLAG_COLUMNS if column in df.columns]

# Progi odrzucania wartości niemożliwych.
MIN_PRICE_PLN = 1000
MAX_MILEAGE_KM = 2_000_000
MIN_YEAR = 1950
MIN_ENGINE_CC = 500
MAX_ENGINE_CC = 8000
MIN_POWER_KM = 20
MAX_POWER_KM = 2000


class CleaningReport:
    """Zbiera i wypisuje efekty kolejnych operacji czyszczenia."""

    def __init__(self, rows_before: int, columns_before: int, input_path: Path) -> None:
        self.input_path = input_path
        self.rows_before = rows_before
        self.columns_before = columns_before
        self.rows_after = rows_before
        self.dropped_rows: list[tuple[str, int]] = []
        self.dropped_columns: list[str] = []
        self.filled: dict[str, tuple[str, int]] = {}

    def drop_rows(self, label: str, count: int) -> None:
        self.dropped_rows.append((label, count))
        self.rows_after -= count

    def drop_columns(self, columns: list[str]) -> None:
        self.dropped_columns.extend(columns)

    def fill(self, column: str, method: str, count: int) -> None:
        self.filled[column] = (method, count)

    def print(self, output: Path, columns_after: int, missing_before: int, missing_after: int) -> None:
        print(f"Plik wejściowy:  {self.input_path}")
        print(f"Plik wyjściowy:  {output}")
        print()
        print(f"Rekordy:  {self.rows_before} -> {self.rows_after}  (usunięto {self.rows_before - self.rows_after})")
        print(f"Kolumny:  {self.columns_before} -> {columns_after}  (usunięto {len(self.dropped_columns)})")
        print()
        print("Wiersze odrzucone:")
        for label, count in self.dropped_rows:
            print(f"  {label}: {count}")
        print()
        print("Kolumny usunięte:")
        for column in self.dropped_columns:
            reason = DROP_COLUMNS.get(column, "kolumna nie występuje w danych")
            print(f"  {column}: {reason}")
        print()
        print(f"Braki w komórkach: {missing_before} -> {missing_after}")
        if self.filled:
            print("Uzupełnione braki:")
            for column, (method, count) in self.filled.items():
                print(f"  {column}: {count} ({method})")
        else:
            print("Uzupełnione braki: brak")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Czyści eksport ogłoszeń Otomoto i zapisuje dane gotowe do trenowania modelu."
    )
    parser.add_argument("input", type=Path, help="ścieżka do pliku CSV z eksportem Otomoto")
    parser.add_argument("output", type=Path, help="ścieżka wynikowego pliku CSV")
    return parser.parse_args()


def same_path(first: Path, second: Path) -> bool:
    """Sprawdza, czy dwie ścieżki wskazują ten sam plik (także przez twardy link)."""
    if first.resolve() == second.resolve():
        return True
    try:
        return first.exists() and second.exists() and first.samefile(second)
    except OSError:
        return False


def strip_text(df: pd.DataFrame) -> None:
    """Przycina białe znaki i zamienia puste napisy na braki."""
    for column in df.columns:
        if df[column].dtype == object:
            values = df[column].astype("string").str.strip()
            df[column] = values.mask(values == "", pd.NA).astype(object)


def to_numeric(df: pd.DataFrame, column: str) -> None:
    if column in df.columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")


def format_dates(df: pd.DataFrame) -> None:
    for column in DATE_COLUMNS:
        if column not in df.columns:
            continue
        dates = pd.to_datetime(df[column], errors="coerce", utc=True)
        df[column] = dates.dt.strftime("%Y-%m-%dT%H:%M:%SZ").astype(object)


def clean(df: pd.DataFrame, reference_year: int, input_path: Path) -> tuple[pd.DataFrame, CleaningReport, int, int]:
    report = CleaningReport(len(df), len(df.columns), input_path)
    missing_before = int(df.isna().sum().sum())

    # 1. Duplikaty ogłoszeń - zostaje pierwsze wystąpienie.
    duplicates = df["id"].duplicated(keep="first") if "id" in df.columns else pd.Series(False, index=df.index)
    report.drop_rows("duplikaty id", int(duplicates.sum()))
    df = df.loc[~duplicates].copy()

    # 2. Waluta - bez kursu wymiany ceny w EUR nie da się porównać z PLN.
    if "currency" in df.columns:
        foreign = df["currency"].notna() & (df["currency"] != "PLN")
        report.drop_rows("waluta inna niż PLN", int(foreign.sum()))
        df = df.loc[~foreign].copy()

    # 3. Brak zmiennej objaśnianej.
    if "price_pln" in df.columns:
        no_price = df["price_pln"].isna()
        report.drop_rows("brak price_pln", int(no_price.sum()))
        df = df.loc[~no_price].copy()

    # 4. Rekordy z dużymi brakami w polach rdzeniowych.
    core = [column for column in CORE_FIELDS if column in df.columns]
    if core:
        share = df[core].isna().mean(axis=1)
        too_empty = share > MAX_CORE_MISSING_SHARE
        report.drop_rows(
            f"ponad {MAX_CORE_MISSING_SHARE:.0%} braków w {len(core)} polach rdzeniowych",
            int(too_empty.sum()),
        )
        df = df.loc[~too_empty].copy()

    # 5. Wartości niemożliwe.
    impossible: list[tuple[str, int]] = []
    checks = [
        ("price_pln", "cena poniżej 1000 PLN", lambda s: s < MIN_PRICE_PLN),
        ("mileage_km", "przebieg powyżej 2 000 000 km", lambda s: s > MAX_MILEAGE_KM),
        ("year", f"rok poza {MIN_YEAR}-{reference_year}", lambda s: (s < MIN_YEAR) | (s > reference_year + 1)),
        (
            "engine_cc",
            f"pojemność poza {MIN_ENGINE_CC}-{MAX_ENGINE_CC} cm3",
            lambda s: (s < MIN_ENGINE_CC) | (s > MAX_ENGINE_CC),
        ),
        (
            "engine_power_km",
            f"moc poza {MIN_POWER_KM}-{MAX_POWER_KM} KM",
            lambda s: (s < MIN_POWER_KM) | (s > MAX_POWER_KM),
        ),
    ]
    for column, label, predicate in checks:
        if column not in df.columns:
            continue
        mask = df[column].notna() & predicate(df[column])
        impossible.append((label, int(mask.sum())))
        df = df.loc[~mask].copy()
    for label, count in impossible:
        report.drop_rows(label, count)

    # 6. Usunięcie kolumn bez wartości dla modelu.
    present = [column for column in DROP_COLUMNS if column in df.columns]
    report.drop_columns(present)
    df = df.drop(columns=present)

    # 7. Normalizacja tekstu i typów.
    strip_text(df)
    for column in NUMERIC_COLUMNS:
        to_numeric(df, column)
    format_dates(df)

    # 8. Flagi 0/1 - wartości spoza zbioru {0, 1} traktujemy jako brak.
    flags = flag_columns(df)
    for column in flags:
        to_numeric(df, column)
        outside = df[column].notna() & ~df[column].isin([0, 1])
        if outside.any():
            df.loc[outside, column] = np.nan
        df[column] = df[column].astype("Int64")

    # 9. Uzupełnienie braków liczbowych medianą.
    for column in MEDIAN_FILL:
        if column not in df.columns:
            continue
        missing = int(df[column].isna().sum())
        if missing:
            df[column] = df[column].fillna(df[column].median())
            report.fill(column, "mediana", missing)

    # 10. Uzupełnienie braków kategorycznych jawną etykietą.
    for column in CATEGORICAL_FILL:
        if column not in df.columns:
            continue
        missing = int(df[column].isna().sum())
        if missing:
            df[column] = df[column].fillna(UNKNOWN_LABEL)
            report.fill(column, f'etykieta "{UNKNOWN_LABEL}"', missing)

    # 11. Flagi - brak deklaracji traktujemy jako 0.
    for column in flags:
        missing = int(df[column].isna().sum())
        if missing:
            df[column] = df[column].fillna(0).astype("Int64")
            report.fill(column, "0 (nie zadeklarowano)", missing)

    # Liczby całkowite tam, gdzie mają sens, żeby CSV nie zawierał "5.0".
    for column in NUMERIC_COLUMNS + flags:
        if column in df.columns and df[column].notna().all():
            df[column] = df[column].astype("int64")

    missing_after = int(df.isna().sum().sum())
    return df, report, missing_before, missing_after


def main() -> int:
    args = parse_args()

    if same_path(args.input, args.output):
        print("Błąd: plik wynikowy nie może być tym samym plikiem co wejściowy.", file=sys.stderr)
        print(f"  input:  {args.input}", file=sys.stderr)
        print(f"  output: {args.output}", file=sys.stderr)
        return 1

    if not args.input.is_file():
        print(f"Błąd: nie znaleziono pliku wejściowego: {args.input}", file=sys.stderr)
        return 1

    df = pd.read_csv(args.input, encoding="utf-8-sig", low_memory=False)

    if "created_at" in df.columns:
        created = pd.to_datetime(df["created_at"], errors="coerce", utc=True)
        reference_year = int(created.dt.year.max()) if created.notna().any() else int(pd.Timestamp.now().year)
    else:
        reference_year = int(pd.Timestamp.now().year)

    df, report, missing_before, missing_after = clean(df, reference_year, args.input)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False, encoding="utf-8-sig")

    report.print(args.output, len(df.columns), missing_before, missing_after)
    print()
    print(f"Zapisano {len(df)} rekordów i {len(df.columns)} kolumn.")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
