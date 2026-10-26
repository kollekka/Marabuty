#!/usr/bin/env python3
"""Przygotowanie danych: czyszczenie i wzbogacenie zbioru ogłoszeń samochodowych.

Uruchomienie:
    python scripts/prepare_data.py data/raw/sample.csv data/processed/sample-clean.csv

Operacje:
1. Usunięcie zbędnych białych znaków z pól tekstowych.
2. Usunięcie powtórzonych ogłoszeń (poza technicznym identyfikatorem `Index`).
3. Ujednolicenie dat do formatu ISO `YYYY-MM-DD` (błędne daty stają się brakami).
4. Konwersja kolumn liczbowych i oznaczenie wartości niemożliwych jako braki.
5. Dodanie kolumn pochodnych: `Displacement_l` (cm³ -> l) oraz `Vehicle_age`.

Skrypt nie usuwa wierszy z powodu braków lub wartości odstających; jedynym
usunięciem są uzasadnione duplikaty. Wynik nie może trafić do pliku wejściowego.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Pola tekstowe, w których usuwamy zbędne białe znaki na początku i końcu.
TEXT_COLUMNS = [
    "Currency",
    "Condition",
    "Vehicle_brand",
    "Vehicle_model",
    "Vehicle_version",
    "Vehicle_generation",
    "Fuel_type",
    "Drive",
    "Transmission",
    "Type",
    "Colour",
    "Origin_country",
    "First_owner",
    "Offer_location",
    "Features",
]

DATE_COLUMNS = ["First_registration_date", "Offer_publication_date"]

NUMERIC_COLUMNS = [
    "Price",
    "Mileage_km",
    "Power_HP",
    "Displacement_cm3",
    "Production_year",
    "Doors_number",
    "CO2_emissions",
]

REFERENCE_YEAR_FALLBACK = 2021


def load_data(path: Path) -> pd.DataFrame:
    """Wczytuje CSV; `utf-8-sig` usuwa ewentualny BOM z nagłówka."""
    if not path.exists():
        raise SystemExit(f"Błąd: plik wejściowy nie istnieje: {path}")
    return pd.read_csv(path, encoding="utf-8-sig", low_memory=False)


def strip_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Usuwa białe znaki z pól tekstowych, nie ruszając braków (NaN)."""
    for column in TEXT_COLUMNS:
        if column in df.columns:
            df[column] = df[column].map(
                lambda value: value.strip() if isinstance(value, str) else value
            )
    return df


def remove_duplicate_ads(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Usuwa powtórzone ogłoszenia.

    Porównujemy wszystkie kolumny poza technicznym `Index`, ponieważ `Index`
    jest unikalnym identyfikatorem wiersza i uniemożliwiłby wykrycie duplikatów.
    """
    subset = [column for column in df.columns if column != "Index"]
    before = len(df)
    df = df.drop_duplicates(subset=subset, keep="first").reset_index(drop=True)
    return df, before - len(df)


def normalize_dates(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, pd.Series]]:
    """Ujednolica daty do ISO (YYYY-MM-DD); błędne daty stają się brakami."""
    parsed_dates: dict[str, pd.Series] = {}
    for column in DATE_COLUMNS:
        if column in df.columns:
            parsed = pd.to_datetime(df[column], dayfirst=True, errors="coerce")
            parsed_dates[column] = parsed
            df[column] = parsed.dt.strftime("%Y-%m-%d")
    return df, parsed_dates


def coerce_numeric_columns(
    df: pd.DataFrame, reference_year: int
) -> tuple[pd.DataFrame, dict[str, int]]:
    """Konwertuje liczby i oznacza wartości niemożliwe jako braki.

    Nie usuwamy wierszy: pojedyncza błędna wartość nie przekreśla całego
    ogłoszenia, a brak można później uzupełnić lub obsłużyć w modelu.
    """
    invalid_counts: dict[str, int] = {}

    for column in NUMERIC_COLUMNS:
        if column in df.columns:
            series = df[column]
            if series.dtype == object:
                series = series.astype("string").str.replace(" ", "", regex=False)
            df[column] = pd.to_numeric(series, errors="coerce")

    rules = {
        "Price": lambda series: series <= 0,
        "Mileage_km": lambda series: series < 0,
        "Power_HP": lambda series: series <= 0,
        "Displacement_cm3": lambda series: series <= 0,
        "Production_year": lambda series: (series < 1900)
        | (series > reference_year + 1),
        "Doors_number": lambda series: series <= 0,
        "CO2_emissions": lambda series: series < 0,
    }

    for column, rule in rules.items():
        if column in df.columns:
            mask = rule(df[column])
            invalid_counts[column] = int(mask.sum())
            df.loc[mask, column] = np.nan

    # Rok produkcji i liczba drzwi są całkowite; rzutowanie na nullable Int64
    # pozwala zachować braki bez zamiany typu na float.
    for column in ["Production_year", "Doors_number"]:
        if column in df.columns:
            df[column] = df[column].round().astype("Int64")

    return df, invalid_counts


def add_derived_columns(
    df: pd.DataFrame,
    parsed_dates: dict[str, pd.Series],
    reference_year: int,
) -> pd.DataFrame:
    """Dodaje przeliczenie jednostek i wskaźnik wieku pojazdu."""
    if "Displacement_cm3" in df.columns:
        df["Displacement_l"] = (df["Displacement_cm3"] / 1000.0).round(3)

    if "Production_year" in df.columns:
        offer_dates = parsed_dates.get("Offer_publication_date")
        if offer_dates is not None and offer_dates.notna().any():
            df["Vehicle_age"] = (
                offer_dates.dt.year - df["Production_year"]
            ).astype("Int64")
        else:
            df["Vehicle_age"] = (
                reference_year - df["Production_year"]
            ).astype("Int64")

    return df


def missing_summary(df: pd.DataFrame, columns: list[str]) -> pd.Series:
    """Zwraca liczbę braków dla wskazanych kolumn (o ile istnieją)."""
    present = [column for column in columns if column in df.columns]
    return df[present].isna().sum()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description=(
            "Czyszczenie zbioru ogłoszeń samochodowych: duplikaty, daty, "
            "typy liczbowe, przeliczenie jednostek i wskaźnik wieku."
        )
    )
    parser.add_argument("input", type=Path, help="Ścieżka do wejściowego pliku CSV")
    parser.add_argument("output", type=Path, help="Ścieżka do wyjściowego pliku CSV")
    args = parser.parse_args()

    input_path = args.input.resolve()
    output_path = args.output.resolve()

    # Zabezpieczenie: nie nadpisujemy danych wejściowych.
    if input_path == output_path:
        print(
            "Błąd: plik wyjściowy nie może być tym samym plikiem co wejściowy.",
            file=sys.stderr,
        )
        return 1

    df = load_data(input_path)
    original_columns = list(df.columns)
    rows_before = len(df)
    missing_before = missing_summary(df, original_columns)

    # 1. Normalizacja tekstu.
    df = strip_text_columns(df)
    # 2. Usunięcie duplikatów.
    df, duplicates_removed = remove_duplicate_ads(df)
    # 3. Ujednolicenie dat.
    df, parsed_dates = normalize_dates(df)

    if (
        "Offer_publication_date" in parsed_dates
        and parsed_dates["Offer_publication_date"].notna().any()
    ):
        reference_year = int(parsed_dates["Offer_publication_date"].dt.year.max())
    else:
        reference_year = REFERENCE_YEAR_FALLBACK

    # 4. Typy liczbowe i oznaczenie wartości niemożliwych jako braki.
    df, invalid_counts = coerce_numeric_columns(df, reference_year)
    # 5. Kolumny pochodne.
    df = add_derived_columns(df, parsed_dates, reference_year)

    rows_after = len(df)
    missing_after = missing_summary(df, original_columns)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8")

    print(f"Wejście:  {input_path}")
    print(f"Wyjście:  {output_path}")
    print(f"Rekordy przed: {rows_before}")
    print(f"Rekordy po:    {rows_after}")
    print(f"Usunięte duplikaty: {duplicates_removed}")
    print(f"Rok odniesienia: {reference_year}")
    print()
    print("Braki w kolumnach źródłowych (przed -> po):")
    for column in original_columns:
        print(
            f"  {column}: {int(missing_before[column])} -> {int(missing_after[column])}"
        )
    print()
    print("Wartości niemożliwe oznaczone jako braki:")
    for column, count in invalid_counts.items():
        print(f"  {column}: {count}")
    print()
    print(f"Kolumny po przetworzeniu ({len(df.columns)}): {', '.join(df.columns)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
