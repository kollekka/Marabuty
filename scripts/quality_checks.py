#!/usr/bin/env python3
"""Automatyczne kontrole jakości wyniku przygotowania danych.

Skrypt sprawdza plik CSV wskazany w argumencie i wypisuje wynik PASS/FAIL
dla każdej kontroli. Kod wyjścia jest różny od zera, jeśli którakolwiek
kontrola nie przejdzie.

Uruchomienie::

    python scripts/quality_checks.py data/processed/sample-clean.csv
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = [
    "id",
    "created_at",
    "make",
    "model",
    "year",
    "mileage_km",
    "price_pln",
    "fuel_type",
    "gearbox",
    "transmission",
    "body_type",
    "city",
    "region",
]

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

BASE_FLAG_COLUMNS = [
    "damaged",
    "registered_pl",
    "first_owner",
    "no_accident",
    "service_aso",
    "imported",
]

KEY_COLUMNS = ["id", "created_at", "price_pln"]

ALLOWED_CATEGORIES = {
    "new_used": {"Używane", "Nowość"},
    "gearbox": {"Manualna", "Automatyczna", "Półautomatyczna"},
}

VALUE_RANGES = {
    "price_pln": (1000, 5_000_000),
    "mileage_km": (0, 2_000_000),
    "year": (1950, datetime.now().year + 1),
    "engine_cc": (500, 8000),
    "engine_power_km": (20, 2000),
}

DATE_PATTERN = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"


class CheckReport:
    """Zlicza kontrole i wypisuje ich wynik."""

    def __init__(self) -> None:
        self.passed = 0
        self.failed = 0

    def check(self, name: str, ok: bool, detail: str) -> None:
        status = "PASS" if ok else "FAIL"
        print(f"{status}  {name}: {detail}")
        if ok:
            self.passed += 1
        else:
            self.failed += 1

    def summary(self) -> int:
        print()
        print(f"Kontrole: {self.passed} PASS, {self.failed} FAIL")
        if self.failed:
            print("Wynik: FAIL")
            return 1
        print("Wynik: PASS")
        return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sprawdza jakość pliku CSV z danymi przygotowanymi do modelowania."
    )
    parser.add_argument("input", type=Path, help="ścieżka do pliku CSV z danymi")
    return parser.parse_args()


def check_record_count(df: pd.DataFrame, report: CheckReport) -> None:
    ok = len(df) > 0 and len(df.columns) > 0
    report.check(
        "Liczba rekordów i kolumn",
        ok,
        f"{len(df)} rekordów, {len(df.columns)} kolumn",
    )


def check_required_columns(df: pd.DataFrame, report: CheckReport) -> None:
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    report.check(
        "Wymagane kolumny",
        not missing,
        "wszystkie obecne" if not missing else f"brak: {', '.join(missing)}",
    )


def check_id(df: pd.DataFrame, report: CheckReport) -> None:
    if "id" not in df.columns:
        report.check("ID niepuste i unikalne", False, "brak kolumny id")
        return
    ids = df["id"]
    blank = int((ids.isna() | ids.astype(str).str.strip().eq("")).sum())
    duplicates = int(ids.duplicated(keep="first").sum())
    unique = int(ids.nunique(dropna=True))
    ok = blank == 0 and duplicates == 0
    report.check(
        "ID niepuste i unikalne",
        ok,
        f"{unique} unikalnych ID, {blank} pustych, {duplicates} duplikatów",
    )


def check_numeric_types(df: pd.DataFrame, report: CheckReport) -> None:
    problems: list[str] = []
    for column in NUMERIC_COLUMNS:
        if column not in df.columns:
            continue
        values = pd.to_numeric(df[column], errors="coerce")
        invalid = int((df[column].notna() & values.isna()).sum())
        if not pd.api.types.is_numeric_dtype(df[column]) or invalid:
            problems.append(f"{column}: {invalid} wartości nieliczbowych")
    report.check(
        "Typy kolumn liczbowych",
        not problems,
        "wszystkie kolumny liczbowe" if not problems else "; ".join(problems),
    )


def check_date_format(df: pd.DataFrame, report: CheckReport) -> None:
    if "created_at" not in df.columns:
        report.check("Format daty created_at", False, "brak kolumny created_at")
        return
    dates = df["created_at"].astype("string")
    matches = dates.str.match(DATE_PATTERN, na=False)
    parsed = pd.to_datetime(dates, errors="coerce", utc=True)
    invalid = int((dates.notna() & (~matches | parsed.isna())).sum())
    report.check(
        "Format daty created_at",
        invalid == 0,
        "wszystkie daty w formacie ISO 8601" if invalid == 0 else f"{invalid} niepoprawnych dat",
    )


def check_value_ranges(df: pd.DataFrame, report: CheckReport) -> None:
    problems: list[str] = []
    for column, (minimum, maximum) in VALUE_RANGES.items():
        if column not in df.columns:
            continue
        values = pd.to_numeric(df[column], errors="coerce")
        outside = df[column].notna() & (
            values.isna() | (values < minimum) | (values > maximum)
        )
        count = int(outside.sum())
        if count:
            problems.append(f"{column}: {count} poza {minimum}-{maximum}")
    report.check(
        "Zakresy wartości",
        not problems,
        "wszystkie wartości w zakresie" if not problems else "; ".join(problems),
    )


def check_categories(df: pd.DataFrame, report: CheckReport) -> None:
    problems: list[str] = []
    for column, allowed in ALLOWED_CATEGORIES.items():
        if column not in df.columns:
            continue
        values = set(df[column].dropna().astype(str))
        invalid = sorted(values - allowed)
        if invalid:
            problems.append(f"{column}: {', '.join(invalid)}")
    report.check(
        "Dozwolone kategorie",
        not problems,
        "wszystkie kategorie dozwolone" if not problems else "; ".join(problems),
    )


def check_flags(df: pd.DataFrame, report: CheckReport) -> None:
    flags = [column for column in df.columns if column.startswith("has_")]
    flags += [column for column in BASE_FLAG_COLUMNS if column in df.columns]
    problems: list[str] = []
    for column in flags:
        values = pd.to_numeric(df[column], errors="coerce")
        invalid = int((df[column].notna() & ~values.isin([0, 1])).sum())
        if invalid:
            problems.append(f"{column}: {invalid}")
    report.check(
        "Flagi 0/1",
        not problems,
        f"{len(flags)} kolumn flag poprawnych" if not problems else "; ".join(problems),
    )


def check_key_completeness(df: pd.DataFrame, report: CheckReport) -> None:
    missing = {
        column: int(df[column].isna().sum())
        for column in KEY_COLUMNS
        if column in df.columns and df[column].isna().any()
    }
    detail = "brak braków" if not missing else ", ".join(
        f"{column}: {count}" for column, count in missing.items()
    )
    report.check("Kompletność kolumn kluczowych", not missing, detail)


def main() -> int:
    args = parse_args()
    report = CheckReport()

    if not args.input.is_file():
        report.check("Wczytanie pliku", False, f"nie znaleziono pliku {args.input}")
        return report.summary()

    try:
        df = pd.read_csv(args.input, encoding="utf-8-sig", low_memory=False)
    except Exception as error:
        report.check("Wczytanie pliku", False, str(error))
        return report.summary()

    report.check("Wczytanie pliku", True, str(args.input))
    check_record_count(df, report)
    check_required_columns(df, report)
    check_id(df, report)
    check_numeric_types(df, report)
    check_date_format(df, report)
    check_value_ranges(df, report)
    check_categories(df, report)
    check_flags(df, report)
    check_key_completeness(df, report)
    return report.summary()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
