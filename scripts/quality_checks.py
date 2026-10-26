#!/usr/bin/env python3
"""Kontrole jakości zbioru ogłoszeń samochodowych.

Uruchomienie:
    python scripts/quality_checks.py data/processed/sample-clean.csv
    python scripts/quality_checks.py data/Car_sale_ads.csv --expected-records 208304
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

IDENTIFIER_COLUMN = "Index"
REFERENCE_YEAR_FALLBACK = 2021

COLUMN_TYPES = {
    "Index": "integer",
    "Price": "numeric",
    "Currency": "text",
    "Condition": "text",
    "Vehicle_brand": "text",
    "Vehicle_model": "text",
    "Vehicle_version": "text",
    "Vehicle_generation": "text",
    "Production_year": "integer",
    "Mileage_km": "numeric",
    "Power_HP": "numeric",
    "Displacement_cm3": "numeric",
    "Fuel_type": "text",
    "CO2_emissions": "numeric",
    "Drive": "text",
    "Transmission": "text",
    "Type": "text",
    "Doors_number": "integer",
    "Colour": "text",
    "Origin_country": "text",
    "First_owner": "text",
    "First_registration_date": "date",
    "Offer_publication_date": "date",
    "Offer_location": "text",
    "Features": "text",
    "Displacement_l": "numeric",
    "Vehicle_age": "integer",
}

OPTIONAL_COLUMNS = {"Displacement_l", "Vehicle_age"}
REQUIRED_COLUMNS = [column for column in COLUMN_TYPES if column not in OPTIONAL_COLUMNS]
DATE_COLUMNS = ["First_registration_date", "Offer_publication_date"]

CATEGORY_RULES = {
    "Currency": {"PLN"},
    "Condition": {"New", "Used"},
    "Transmission": {"Manual", "Automatic"},
    "Drive": {
        "Front wheels",
        "Rear wheels",
        "4x4 (permanent)",
        "4x4 (attached automatically)",
        "4x4 (attached manually)",
    },
}

NUMERIC_RULES = {
    "Price": (lambda series: series <= 0, "> 0"),
    "Mileage_km": (lambda series: series < 0, ">= 0"),
    "Power_HP": (lambda series: series <= 0, "> 0"),
    "Displacement_cm3": (lambda series: series <= 0, "> 0"),
    "Doors_number": (lambda series: series <= 0, "> 0"),
    "CO2_emissions": (lambda series: series < 0, ">= 0"),
    "Displacement_l": (lambda series: series <= 0, "> 0"),
    "Vehicle_age": (lambda series: series < 0, ">= 0"),
}


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str = ""


def _non_empty(series: pd.Series) -> pd.Series:
    text = series.astype("string").str.strip()
    return series.notna() & text.ne("").fillna(False)


def _to_numeric(series: pd.Series) -> pd.Series:
    text = series.astype("string").str.replace(" ", "", regex=False)
    return pd.to_numeric(text, errors="coerce")


def _to_date(series: pd.Series) -> pd.Series:
    text = series.astype("string").str.strip()
    iso = pd.to_datetime(text, format="%Y-%m-%d", errors="coerce")
    european = pd.to_datetime(text, format="%d/%m/%Y", errors="coerce")
    return iso.fillna(european)


def _reference_year(df: pd.DataFrame) -> int:
    if "Offer_publication_date" in df.columns:
        dates = _to_date(df["Offer_publication_date"])
        if dates.notna().any():
            return int(dates.dt.year.max())
    return REFERENCE_YEAR_FALLBACK


def _check_column_type(series: pd.Series, expected: str) -> str | None:
    if expected in {"numeric", "integer"}:
        converted = _to_numeric(series)
        invalid = _non_empty(series) & converted.isna()
        if invalid.any():
            return f"niepoprawne wartości liczbowe: {int(invalid.sum())}"
        if expected == "integer":
            fractional = converted.notna() & (converted % 1 != 0)
            if fractional.any():
                return f"niecałkowite wartości: {int(fractional.sum())}"
        return None

    if expected == "date":
        invalid = _non_empty(series) & _to_date(series).isna()
        if invalid.any():
            return f"niepoprawne daty: {int(invalid.sum())}"
        return None

    if expected == "text":
        values = series[_non_empty(series)]
        if values.empty:
            return None
        non_text = ~values.map(lambda value: isinstance(value, str))
        if non_text.any():
            return f"niepoprawne wartości tekstowe: {int(non_text.sum())}"
        return None

    return f"nieznany oczekiwany typ: {expected}"


def check_required_columns(df: pd.DataFrame) -> CheckResult:
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        return CheckResult(
            "Wymagane kolumny",
            False,
            "brakuje: " + ", ".join(missing),
        )
    return CheckResult(
        "Wymagane kolumny",
        True,
        f"{len(REQUIRED_COLUMNS)} kolumn obecnych",
    )


def check_record_count(
    df: pd.DataFrame, min_records: int, expected_records: int | None
) -> CheckResult:
    if expected_records is not None:
        passed = len(df) == expected_records
        detail = f"{len(df)} rekordów (oczekiwano {expected_records})"
    else:
        passed = len(df) >= min_records
        detail = f"{len(df)} rekordów (minimum {min_records})"
    return CheckResult("Liczba rekordów", passed, detail)


def check_column_types(df: pd.DataFrame) -> CheckResult:
    issues = []
    checked = 0

    for column, expected in COLUMN_TYPES.items():
        if column not in df.columns:
            if column in REQUIRED_COLUMNS:
                issues.append(f"{column}: brak kolumny")
            continue

        checked += 1
        issue = _check_column_type(df[column], expected)
        if issue:
            issues.append(f"{column}: {issue}")

    if issues:
        detail = "; ".join(issues[:8])
        if len(issues) > 8:
            detail += f"; ... ({len(issues) - 8} więcej)"
        return CheckResult("Typy kolumn", False, detail)

    return CheckResult(
        "Typy kolumn",
        True,
        f"{checked} kolumn zgodnych z typem logicznym",
    )


def check_identifier(df: pd.DataFrame) -> CheckResult:
    if IDENTIFIER_COLUMN not in df.columns:
        return CheckResult("ID", False, f"brak kolumny {IDENTIFIER_COLUMN}")

    series = df[IDENTIFIER_COLUMN]
    non_empty = _non_empty(series)
    missing = int((~non_empty).sum())
    duplicate_rows = int((series.duplicated(keep=False) & non_empty).sum())

    problems = []
    if missing:
        problems.append(f"puste wartości: {missing}")
    if duplicate_rows:
        problems.append(f"wiersze z powtórzonym ID: {duplicate_rows}")

    if problems:
        return CheckResult("ID", False, "; ".join(problems))

    return CheckResult(
        "ID",
        True,
        f"{int(non_empty.sum())} niepustych i unikalnych wartości",
    )


def check_duplicate_rows(df: pd.DataFrame) -> CheckResult:
    subset = [column for column in df.columns if column != IDENTIFIER_COLUMN]
    if not subset:
        return CheckResult("Duplikaty ogłoszeń", False, "brak kolumn do porównania")

    duplicates = int(df.duplicated(subset=subset).sum())
    if duplicates:
        return CheckResult(
            "Duplikaty ogłoszeń",
            False,
            f"powtórzone wiersze (bez {IDENTIFIER_COLUMN}): {duplicates}",
        )
    return CheckResult("Duplikaty ogłoszeń", True, "0 duplikatów")


def check_numeric_ranges(df: pd.DataFrame) -> CheckResult:
    issues = []
    checked = 0

    for column, (rule, expected_range) in NUMERIC_RULES.items():
        if column not in df.columns:
            if column in REQUIRED_COLUMNS:
                issues.append(f"{column}: brak kolumny")
            continue

        checked += 1
        numeric = _to_numeric(df[column])
        violations = int((numeric.notna() & rule(numeric)).sum())
        if violations:
            issues.append(
                f"{column}: wartości poza zakresem: {violations} "
                f"({expected_range})"
            )

    if "Production_year" in df.columns:
        checked += 1
        numeric = _to_numeric(df["Production_year"])
        reference_year = _reference_year(df)
        invalid = numeric.notna() & (
            (numeric < 1900) | (numeric > reference_year + 1)
        )
        if invalid.any():
            issues.append(
                "Production_year: "
                f"wartości poza zakresem: {int(invalid.sum())} "
                f"(1900–{reference_year + 1})"
            )
    else:
        issues.append("Production_year: brak kolumny")

    if issues:
        detail = "; ".join(issues[:8])
        if len(issues) > 8:
            detail += f"; ... ({len(issues) - 8} więcej)"
        return CheckResult("Zakresy liczb", False, detail)

    return CheckResult(
        "Zakresy liczb",
        True,
        f"sprawdzono {checked} kolumn; brak naruszeń",
    )


def check_categories(df: pd.DataFrame) -> CheckResult:
    issues = []
    checked = 0

    for column, allowed in CATEGORY_RULES.items():
        if column not in df.columns:
            if column in REQUIRED_COLUMNS:
                issues.append(f"{column}: brak kolumny")
            continue

        checked += 1
        values = df[column].dropna().astype("string").str.strip()
        values = values[values.ne("").fillna(False)]
        unexpected = sorted(set(values.tolist()) - allowed)
        if unexpected:
            preview = ", ".join(repr(value) for value in unexpected[:5])
            if len(unexpected) > 5:
                preview += f", ... ({len(unexpected) - 5} więcej)"
            issues.append(f"{column}: nieznane wartości: {preview}")

    if issues:
        detail = "; ".join(issues[:8])
        if len(issues) > 8:
            detail += f"; ... ({len(issues) - 8} więcej)"
        return CheckResult("Kategorie", False, detail)

    return CheckResult(
        "Kategorie",
        True,
        f"sprawdzono {checked} kolumn; wszystkie wartości dozwolone",
    )


def check_dates(df: pd.DataFrame) -> CheckResult:
    issues = []
    checked = 0

    for column in DATE_COLUMNS:
        if column not in df.columns:
            issues.append(f"{column}: brak kolumny")
            continue

        checked += 1
        non_empty = _non_empty(df[column])
        parsed = _to_date(df[column])
        invalid = int((non_empty & parsed.isna()).sum())
        missing = int((~non_empty).sum())
        if invalid:
            issues.append(
                f"{column}: niepoprawne daty: {invalid} (braki: {missing})"
            )

    if issues:
        return CheckResult("Daty", False, "; ".join(issues))

    return CheckResult(
        "Daty",
        True,
        f"sprawdzono {checked} kolumn; brak błędnych dat",
    )


def run_checks(
    df: pd.DataFrame, min_records: int, expected_records: int | None
) -> list[CheckResult]:
    return [
        check_required_columns(df),
        check_record_count(df, min_records, expected_records),
        check_column_types(df),
        check_identifier(df),
        check_duplicate_rows(df),
        check_numeric_ranges(df),
        check_categories(df),
        check_dates(df),
    ]


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Kontrole jakości zbioru CSV.")
    parser.add_argument("input", type=Path, help="Ścieżka do pliku CSV")
    parser.add_argument(
        "--min-records",
        type=int,
        default=1,
        help="Minimalna liczba rekordów (domyślnie 1)",
    )
    parser.add_argument(
        "--expected-records",
        type=int,
        default=None,
        help="Oczekiwana liczba rekordów; jeśli podana, sprawdzana jest równość",
    )
    args = parser.parse_args()

    if args.min_records < 0:
        parser.error("--min-records nie może być ujemne")
    if args.expected_records is not None and args.expected_records < 0:
        parser.error("--expected-records nie może być ujemne")

    if not args.input.exists():
        print(f"[FAIL] Wczytanie pliku — plik nie istnieje: {args.input}")
        return 2

    try:
        df = pd.read_csv(args.input, encoding="utf-8-sig", low_memory=False)
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError) as exc:
        print(f"[FAIL] Wczytanie pliku — {exc}")
        return 2

    print(f"Plik: {args.input}")
    print(f"Rekordy: {len(df)}")
    print(f"Kolumny: {len(df.columns)}")
    print()

    results = run_checks(df, args.min_records, args.expected_records)
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        detail = f" — {result.detail}" if result.detail else ""
        print(f"[{status}] {result.name}{detail}")

    passed = sum(result.passed for result in results)
    overall = "PASS" if passed == len(results) else "FAIL"
    print()
    print(f"Wynik: {overall} ({passed}/{len(results)})")

    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
