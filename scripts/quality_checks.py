#!/usr/bin/env python3
"""Podstawowa kontrola jakości przetworzonego zbioru CSV.

Uruchomienie:
    python scripts/quality_checks.py data/processed/sample-clean.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def main() -> int:
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Kontrola jakości zbioru CSV.")
    parser.add_argument("input", type=Path, help="Ścieżka do pliku CSV")
    args = parser.parse_args()

    if not args.input.exists():
        raise SystemExit(f"Błąd: plik nie istnieje: {args.input}")

    df = pd.read_csv(args.input, encoding="utf-8-sig", low_memory=False)
    print(f"Plik: {args.input}")
    print(f"Rekordy: {len(df)}")
    print(f"Kolumny: {len(df.columns)}")

    key_columns = [column for column in df.columns if column != "Index"]
    duplicates = int(df.duplicated(subset=key_columns).sum())
    print(f"Duplikaty (bez Index): {duplicates}")

    missing = df.isna().sum().sort_values(ascending=False)
    print("Braki (kolumna: liczba):")
    any_missing = False
    for column, count in missing.items():
        if count > 0:
            any_missing = True
            print(f"  {column}: {int(count)}")
    if not any_missing:
        print("  brak")

    if "Price" in df.columns:
        print(f"Price <= 0: {int((df['Price'] <= 0).sum())}")
    if "Production_year" in df.columns:
        print(
            "Production_year poza zakresem 1900+: "
            f"{int((df['Production_year'] < 1900).sum())}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
