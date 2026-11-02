#!/usr/bin/env python3
"""Kontrole formatu i spójności wyników porównania metod (Lab 4).

Skrypt czyta ``comparison.csv`` i ``observations.csv`` z podanych katalogów
i sprawdza zgodność z kontraktem oraz arytmetykę metryk. Każda kontrola
wypisuje PASS/FAIL, a kod wyjścia jest różny od zera przy naruszeniu.

Uruchomienie::

    python scripts/check_results.py results/lab4 results/lab4/sensitivity
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

COMPARISON_COLUMNS = [
    "split",
    "test_size",
    "seed",
    "method",
    "n_train",
    "n_test",
    "mae_pln",
    "rmse_pln",
    "r2",
    "mape_pct",
]

OBSERVATION_COLUMNS = [
    "split",
    "row_index",
    "id",
    "make",
    "model",
    "year",
    "mileage_km",
    "price_pln",
    "baseline_pred_pln",
    "model_pred_pln",
    "baseline_abs_error_pln",
    "model_abs_error_pln",
    "baseline_ape_pct",
    "model_ape_pct",
]

METHODS = {"baseline", "ridge"}
ARITHMETIC_TOLERANCE = 0.02
METRICS_TOLERANCE = 0.01


class CheckReport:
    """Zlicza i wypisuje kontrole dla jednego katalogu."""

    def __init__(self, directory: Path) -> None:
        self.directory = directory
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
        description="Sprawdza format i spójność wyników porównania metod."
    )
    parser.add_argument(
        "directories",
        nargs="*",
        type=Path,
        default=[Path("results/lab4")],
        help="katalogi z comparison.csv i observations.csv",
    )
    parser.add_argument(
        "--expected-rows",
        type=int,
        default=25,
        help="oczekiwana liczba rekordów wejściowych (domyślnie 25)",
    )
    return parser.parse_args()


def compare_columns(actual: list[str], expected: list[str]) -> tuple[bool, str]:
    missing = [column for column in expected if column not in actual]
    extra = [column for column in actual if column not in expected]
    if missing or extra:
        parts = []
        if missing:
            parts.append(f"brak: {', '.join(missing)}")
        if extra:
            parts.append(f"nadmiar: {', '.join(extra)}")
        return False, "; ".join(parts)
    if actual != expected:
        return False, "kolumny w innej kolejności niż w kontrakcie"
    return True, "zgodne z kontraktem"


def check_methods(comparison: pd.DataFrame, report: CheckReport) -> bool:
    if "method" not in comparison.columns:
        report.check("Metody i wiersze", False, "brak kolumny method")
        return False
    counts = comparison["method"].value_counts()
    ok = set(counts.index) == METHODS and all(int(value) == 1 for value in counts)
    detail = ", ".join(f"{method}: {int(counts.get(method, 0))}" for method in sorted(METHODS))
    report.check("Metody i wiersze", bool(ok), detail)
    return bool(ok)


def check_case_count(
    comparison: pd.DataFrame, observations: pd.DataFrame, report: CheckReport, expected_rows: int
) -> bool:
    needed = {"n_train", "n_test"}
    if not needed.issubset(comparison.columns):
        report.check("Liczba przypadków", False, "brak kolumn n_train lub n_test")
        return False
    n_train = comparison["n_train"].tolist()
    n_test = comparison["n_test"].tolist()
    same_train = len(set(n_train)) == 1
    same_test = len(set(n_test)) == 1
    obs_count = len(observations)
    count_matches = bool(same_test and int(n_test[0]) == obs_count)
    total_matches = bool(same_train and int(n_train[0]) + int(n_test[0]) == expected_rows)
    ok = same_train and same_test and count_matches and total_matches
    detail = (
        f"n_train={n_train}, n_test={n_test}, observations={obs_count}, "
        f"oczekiwane łącznie={expected_rows}"
    )
    report.check("Liczba przypadków", ok, detail)
    return ok


def check_missing_and_unique(comparison: pd.DataFrame, observations: pd.DataFrame, report: CheckReport) -> None:
    missing = int(comparison.isna().sum().sum() + observations.isna().sum().sum())
    unique_ok = True
    duplicate_details = []
    for column in ("row_index", "id"):
        if column in observations.columns:
            duplicates = int(observations[column].duplicated(keep="first").sum())
            if duplicates:
                unique_ok = False
                duplicate_details.append(f"{column}: {duplicates} duplikatów")
        else:
            unique_ok = False
            duplicate_details.append(f"brak kolumny {column}")
    ok = missing == 0 and unique_ok
    detail = f"braki: {missing}"
    if duplicate_details:
        detail += "; " + "; ".join(duplicate_details)
    else:
        detail += "; row_index i id unikalne"
    report.check("Braki i unikalność", ok, detail)


def check_signs_and_units(comparison: pd.DataFrame, observations: pd.DataFrame, report: CheckReport) -> None:
    problems = []
    positive_columns = ["price_pln", "baseline_pred_pln", "model_pred_pln"]
    nonnegative_columns = [
        "baseline_abs_error_pln",
        "model_abs_error_pln",
        "baseline_ape_pct",
        "model_ape_pct",
    ]
    for column in positive_columns:
        if column not in observations.columns:
            problems.append(f"brak {column}")
            continue
        values = pd.to_numeric(observations[column], errors="coerce")
        if values.isna().any() or (values <= 0).any():
            problems.append(f"{column}: wartości <= 0 lub nieliczbowe")
    for column in nonnegative_columns:
        if column not in observations.columns:
            problems.append(f"brak {column}")
            continue
        values = pd.to_numeric(observations[column], errors="coerce")
        if values.isna().any() or (values < 0).any():
            problems.append(f"{column}: wartości < 0 lub nieliczbowe")
    for column in ("mae_pln", "rmse_pln", "mape_pct"):
        if column not in comparison.columns:
            problems.append(f"brak {column}")
            continue
        values = pd.to_numeric(comparison[column], errors="coerce")
        if values.isna().any() or (values < 0).any():
            problems.append(f"{column}: wartości < 0 lub nieliczbowe")
    if "r2" not in comparison.columns:
        problems.append("brak r2")
    else:
        r2 = pd.to_numeric(comparison["r2"], errors="coerce")
        if r2.isna().any() or (r2 > 1).any():
            problems.append("r2: wartości > 1 lub nieliczbowe")
    report.check(
        "Znaki i jednostki",
        not problems,
        "ceny i prognozy > 0, błędy i procenty >= 0, R2 <= 1"
        if not problems
        else "; ".join(problems),
    )


def check_error_arithmetic(observations: pd.DataFrame, report: CheckReport) -> None:
    needed = {
        "price_pln",
        "baseline_pred_pln",
        "model_pred_pln",
        "baseline_abs_error_pln",
        "model_abs_error_pln",
        "baseline_ape_pct",
        "model_ape_pct",
    }
    if not needed.issubset(observations.columns):
        report.check("Arytmetyka błędów", False, "brak wymaganych kolumn")
        return
    price = observations["price_pln"].to_numpy(dtype=float)
    differences = []
    for prefix in ("baseline", "model"):
        prediction = observations[f"{prefix}_pred_pln"].to_numpy(dtype=float)
        error = observations[f"{prefix}_abs_error_pln"].to_numpy(dtype=float)
        ape = observations[f"{prefix}_ape_pct"].to_numpy(dtype=float)
        differences.append(float(np.max(np.abs(error - np.abs(price - prediction)))))
        differences.append(float(np.max(np.abs(ape - np.abs(price - prediction) / price * 100))))
    maximum = max(differences)
    report.check(
        "Arytmetyka błędów",
        maximum <= ARITHMETIC_TOLERANCE,
        f"maksymalna różnica {maximum:.4f} (tolerancja {ARITHMETIC_TOLERANCE})",
    )


def check_aggregate_metrics(comparison: pd.DataFrame, observations: pd.DataFrame, report: CheckReport) -> None:
    needed = {"method", "mae_pln", "rmse_pln", "r2", "mape_pct"}
    if not needed.issubset(comparison.columns):
        report.check("Metryki zbiorcze", False, "brak wymaganych kolumn w comparison.csv")
        return
    if not {"price_pln", "baseline_pred_pln", "model_pred_pln"}.issubset(observations.columns):
        report.check("Metryki zbiorcze", False, "brak wymaganych kolumn w observations.csv")
        return
    actual = observations["price_pln"].to_numpy(dtype=float)
    maximum = 0.0
    for _, row in comparison.iterrows():
        method = str(row["method"])
        prediction_column = f"{'baseline' if method == 'baseline' else 'model'}_pred_pln"
        if prediction_column not in observations.columns:
            maximum = float("inf")
            break
        predicted = observations[prediction_column].to_numpy(dtype=float)
        errors = actual - predicted
        mae = float(np.mean(np.abs(errors)))
        rmse = float(np.sqrt(np.mean(errors**2)))
        ss_res = float(np.sum(errors**2))
        ss_tot = float(np.sum((actual - actual.mean()) ** 2))
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
        mape = float(np.mean(np.abs(errors / actual)) * 100)
        for name, computed in (
            ("mae_pln", mae),
            ("rmse_pln", rmse),
            ("r2", r2),
            ("mape_pct", mape),
        ):
            maximum = max(maximum, abs(float(row[name]) - computed))
    report.check(
        "Metryki zbiorcze",
        maximum <= METRICS_TOLERANCE,
        f"maksymalna różnica {maximum:.4f} (tolerancja {METRICS_TOLERANCE})",
    )


def check_metadata(comparison: pd.DataFrame, observations: pd.DataFrame, report: CheckReport) -> None:
    needed = {"split", "test_size", "seed"}
    if not needed.issubset(comparison.columns) or "split" not in observations.columns:
        report.check("Metadane", False, "brak kolumn split, test_size lub seed")
        return
    splits = set(comparison["split"].astype(str))
    test_sizes = set(comparison["test_size"].astype(float))
    seeds = set(comparison["seed"].astype(int))
    observation_splits = set(observations["split"].astype(str))
    test_size = next(iter(test_sizes)) if test_sizes else float("nan")
    ok = (
        len(splits) == 1
        and len(test_sizes) == 1
        and len(seeds) == 1
        and len(observation_splits) == 1
        and splits == observation_splits
        and 0 < test_size < 1
    )
    detail = (
        f"split={sorted(splits)}, test_size={sorted(test_sizes)}, "
        f"seed={sorted(seeds)}, observations_split={sorted(observation_splits)}"
    )
    report.check("Metadane", ok, detail)


def run_directory(directory: Path, expected_rows: int) -> int:
    print(f"=== {directory} ===")
    report = CheckReport(directory)
    comparison_path = directory / "comparison.csv"
    observations_path = directory / "observations.csv"

    missing = [str(path) for path in (comparison_path, observations_path) if not path.is_file()]
    if missing:
        report.check("Pliki i wczytanie", False, f"brak plików: {', '.join(missing)}")
        return report.summary()

    try:
        comparison = pd.read_csv(comparison_path, encoding="utf-8-sig", low_memory=False)
        observations = pd.read_csv(observations_path, encoding="utf-8-sig", low_memory=False)
    except Exception as error:
        report.check("Pliki i wczytanie", False, str(error))
        return report.summary()

    report.check(
        "Pliki i wczytanie",
        True,
        f"comparison.csv ({len(comparison)} wiersze), observations.csv ({len(observations)} wierszy)",
    )

    comparison_ok = compare_columns(list(comparison.columns), COMPARISON_COLUMNS)
    report.check("Kolumny comparison", comparison_ok[0], comparison_ok[1])
    observations_ok = compare_columns(list(observations.columns), OBSERVATION_COLUMNS)
    report.check("Kolumny observations", observations_ok[0], observations_ok[1])

    if not comparison_ok[0] or not observations_ok[0]:
        report.check("Metody i wiersze", False, "pominięto z powodu niezgodnych kolumn")
        report.check("Liczba przypadków", False, "pominięto z powodu niezgodnych kolumn")
        report.check("Braki i unikalność", False, "pominięto z powodu niezgodnych kolumn")
        report.check("Znaki i jednostki", False, "pominięto z powodu niezgodnych kolumn")
        report.check("Arytmetyka błędów", False, "pominięto z powodu niezgodnych kolumn")
        report.check("Metryki zbiorcze", False, "pominięto z powodu niezgodnych kolumn")
        report.check("Metadane", False, "pominięto z powodu niezgodnych kolumn")
        return report.summary()

    check_methods(comparison, report)
    check_case_count(comparison, observations, report, expected_rows)
    check_missing_and_unique(comparison, observations, report)
    check_signs_and_units(comparison, observations, report)
    check_error_arithmetic(observations, report)
    check_aggregate_metrics(comparison, observations, report)
    check_metadata(comparison, observations, report)
    return report.summary()


def main() -> int:
    args = parse_args()
    directories = args.directories or [Path("results/lab4")]
    exit_code = 0
    for directory in directories:
        report_result = run_directory(directory, args.expected_rows)
        exit_code = max(exit_code, report_result)
        print()
    print(f"Sprawdzono katalogi: {len(directories)}")
    print("Wynik końcowy: PASS" if exit_code == 0 else "Wynik końcowy: FAIL")
    return exit_code


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
