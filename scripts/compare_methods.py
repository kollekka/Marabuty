#!/usr/bin/env python3
"""Porównanie baseline i regresji Ridge na próbce ogłoszeń Otomoto (Lab 4).

Kontrakt eksperymentu opisuje ``docs/experiment.md``:

- dane: ``data/processed/sample-clean.csv``,
- cel: ``price_pln``,
- baseline: mediana ceny dla pary ``make``+``model``, potem dla ``make``,
  a na końcu mediana globalna; wszystkie mediany liczone tylko na train,
- model: ``Ridge(alpha=1.0)`` na ``log1p(price_pln)``,
- metryki: MAE, RMSE, R^2 i MAPE liczone na teście.

Miejsca, w których mogłaby wyciec informacja z testu, są zamknięte:

1. imputacja, kodowanie i dopasowanie modelu widzą wyłącznie train,
2. mediany baseline liczone są wyłącznie na train,
3. ``alpha`` jest ustalona z góry i nie jest strojona na teście,
4. ``id``, ``created_at`` i dane sprzedawcy nie wchodzą do modelu,
5. metryki liczone są wyłącznie na teście.

Uruchomienie::

    python scripts/compare_methods.py data/processed/sample-clean.csv \
        --output-dir results/lab4 --test-size 0.2 --seed 42

Próba wrażliwości (zmienia się tylko ``--test-size``)::

    python scripts/compare_methods.py data/processed/sample-clean.csv \
        --output-dir results/lab4/sensitivity --test-size 0.3 --seed 42
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

TARGET = "price_pln"

# Predyktory z kontraktu. ``city`` pomijamy, bo rozjeżdża wymiar po kodowaniu,
# a ``generation`` i flagi ``has_*`` - z powodu braków i ryzyka przeuczenia.
NUMERIC_FEATURES = ["year", "mileage_km", "engine_cc", "engine_power_km"]
CATEGORICAL_FEATURES = [
    "make",
    "model",
    "fuel_type",
    "gearbox",
    "transmission",
    "body_type",
    "new_used",
    "region",
]

REQUIRED_COLUMNS = [TARGET] + NUMERIC_FEATURES + CATEGORICAL_FEATURES

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

MIN_ROWS = 10
MIN_TEST_ROWS = 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Porównuje baseline mediany z regresją Ridge na próbce Otomoto."
    )
    parser.add_argument("input", type=Path, help="plik CSV z oczyszczonymi danymi")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/lab4"),
        help="katalog na comparison.csv i observations.csv (domyślnie results/lab4)",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="udział zbioru testowego; 0.2 to podział 80/20 z kontraktu",
    )
    parser.add_argument("--seed", type=int, default=42, help="ziarno podziału (domyślnie 42)")
    parser.add_argument(
        "--alpha",
        type=float,
        default=1.0,
        help="kara L2 regresji Ridge; wartość z kontraktu to 1.0 i nie jest strojona",
    )
    return parser.parse_args()


def same_path(first: Path, second: Path) -> bool:
    """Sprawdza, czy dwie ścieżki wskazują ten sam plik."""
    if first.resolve() == second.resolve():
        return True
    try:
        return first.exists() and second.exists() and first.samefile(second)
    except OSError:
        return False


def split_label(test_size: float) -> str:
    train_share = int(round((1 - test_size) * 100))
    test_share = int(round(test_size * 100))
    return f"{train_share}_{test_share}"


def compute_metrics(actual: np.ndarray, predicted: np.ndarray) -> dict[str, float]:
    """Liczy MAE, RMSE, R^2 i MAPE bezpośrednio ze wzorów."""
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    errors = actual - predicted

    mae = float(np.mean(np.abs(errors)))
    rmse = float(np.sqrt(np.mean(errors**2)))

    ss_res = float(np.sum(errors**2))
    ss_tot = float(np.sum((actual - actual.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")

    positive = actual > 0
    mape = float(np.mean(np.abs(errors[positive] / actual[positive])) * 100) if positive.any() else float("nan")

    return {"mae_pln": mae, "rmse_pln": rmse, "r2": r2, "mape_pct": mape}


def self_check_metrics() -> None:
    """Pokazuje wzory na trzech liczbach i porównuje wynik ze sklearn."""
    actual = np.array([100.0, 200.0, 300.0])
    predicted = np.array([110.0, 180.0, 330.0])

    own = compute_metrics(actual, predicted)
    reference = {
        "mae_pln": mean_absolute_error(actual, predicted),
        "rmse_pln": float(np.sqrt(mean_squared_error(actual, predicted))),
        "r2": r2_score(actual, predicted),
        "mape_pct": float(np.mean(np.abs((actual - predicted) / actual)) * 100),
    }

    print("Kontrola metryk na 3 liczbach:")
    print(f"  cena rzeczywista: {actual.tolist()}, prognoza: {predicted.tolist()}")
    print(f"  MAE  = mean(|y - yhat|)            = {own['mae_pln']:.2f} PLN")
    print(f"  RMSE = sqrt(mean((y - yhat)^2))    = {own['rmse_pln']:.2f} PLN")
    print(f"  R2   = 1 - SS_res / SS_tot         = {own['r2']:.4f}")
    print(f"  MAPE = mean(|y - yhat| / y) * 100  = {own['mape_pct']:.2f} %")

    for key, value in own.items():
        if not np.isclose(value, reference[key], rtol=1e-9, atol=1e-9):
            raise AssertionError(f"Metryka {key} niezgodna ze sklearn: {value} != {reference[key]}")
    print("  zgodność ze sklearn.metrics: tak")
    print()


def build_model(alpha: float) -> Pipeline:
    """Pipeline: imputacja i kodowanie dopasowane tylko na train."""
    numeric = Pipeline([("imputer", SimpleImputer(strategy="median"))])
    categorical = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "onehot",
                OneHotEncoder(handle_unknown="ignore", min_frequency=2, sparse_output=False),
            ),
        ]
    )
    preprocess = ColumnTransformer(
        [
            ("num", numeric, NUMERIC_FEATURES),
            ("cat", categorical, CATEGORICAL_FEATURES),
        ]
    )
    return Pipeline([("preprocess", preprocess), ("ridge", Ridge(alpha=alpha))])


def baseline_predictions(train: pd.DataFrame, test: pd.DataFrame) -> np.ndarray:
    """Mediana z train dla make+model, potem make, na końcu mediana globalna."""
    global_median = float(train[TARGET].median())
    pair_median = train.groupby(["make", "model"])[TARGET].median()
    make_median = train.groupby("make")[TARGET].median()

    pair_index = pd.MultiIndex.from_frame(test[["make", "model"]])
    predictions = pd.Series(pair_median.reindex(pair_index).to_numpy(dtype=float), index=test.index)
    predictions = predictions.fillna(test["make"].map(make_median).astype(float))
    predictions = predictions.fillna(global_median)
    return predictions.to_numpy(dtype=float)


def validate_input(df: pd.DataFrame, test_size: float) -> None:
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Brak wymaganych kolumn: {', '.join(missing_columns)}")

    if not 0 < test_size < 1:
        raise ValueError("--test-size musi być w przedziale (0, 1)")

    if len(df) < MIN_ROWS:
        raise ValueError(f"Za mało rekordów: {len(df)}, wymagane co najmniej {MIN_ROWS}")

    missing_values = df[REQUIRED_COLUMNS].isna().sum()
    if int(missing_values.sum()) > 0:
        columns = ", ".join(missing_values[missing_values > 0].index)
        raise ValueError(f"Braki wartości w kolumnach: {columns}; uruchom najpierw scripts/prepare_data.py")

    if (df[TARGET] <= 0).any():
        raise ValueError("Kolumna price_pln zawiera ceny niedodatnie, MAPE byłoby nieokreślone")


def run(df: pd.DataFrame, args: argparse.Namespace, split: str, train: pd.DataFrame, test: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    baseline_pred = baseline_predictions(train, test)

    model = build_model(alpha=args.alpha)
    model.fit(train[NUMERIC_FEATURES + CATEGORICAL_FEATURES], np.log1p(train[TARGET].to_numpy()))
    model_pred = np.expm1(model.predict(test[NUMERIC_FEATURES + CATEGORICAL_FEATURES]))

    # log1p/expm1 może teoretycznie dać wartość niedodatnią; tniemy ją do 1 PLN.
    non_positive = int((model_pred <= 0).sum())
    if non_positive:
        model_pred = np.clip(model_pred, 1.0, None)
        print(f"Uwaga: {non_positive} prognoz modelu <= 0 PLN podniesiono do 1 PLN.")

    actual = test[TARGET].to_numpy(dtype=float)

    comparison_rows = []
    for method, predictions in (("baseline", baseline_pred), ("ridge", model_pred)):
        metrics = compute_metrics(actual, predictions)
        comparison_rows.append(
            {
                "split": split,
                "test_size": args.test_size,
                "seed": args.seed,
                "method": method,
                "n_train": len(train),
                "n_test": len(test),
                **metrics,
            }
        )
    comparison = pd.DataFrame(comparison_rows, columns=COMPARISON_COLUMNS)

    baseline_error = np.abs(actual - baseline_pred)
    model_error = np.abs(actual - model_pred)
    observations = pd.DataFrame(
        {
            "split": split,
            "row_index": test.index,
            "id": test["id"].to_numpy(),
            "make": test["make"].to_numpy(),
            "model": test["model"].to_numpy(),
            "year": test["year"].to_numpy(),
            "mileage_km": test["mileage_km"].to_numpy(),
            TARGET: actual,
            "baseline_pred_pln": baseline_pred,
            "model_pred_pln": model_pred,
            "baseline_abs_error_pln": baseline_error,
            "model_abs_error_pln": model_error,
            "baseline_ape_pct": baseline_error / actual * 100,
            "model_ape_pct": model_error / actual * 100,
        },
        columns=OBSERVATION_COLUMNS,
    ).sort_values("row_index").reset_index(drop=True)

    # Asercje spójności wyniku.
    assert len(train) + len(test) == len(df), "podział nie pokrywa wszystkich rekordów"
    assert len(observations) == len(test), "liczba obserwacji różni się od liczby wierszy testu"
    assert observations["baseline_pred_pln"].gt(0).all(), "baseline zwrócił prognozę <= 0"
    assert observations["model_pred_pln"].gt(0).all(), "model zwrócił prognozę <= 0"
    assert not observations.isna().any().any(), "w observations.csv są braki"
    assert not comparison.isna().any().any(), "w comparison.csv są braki"

    return comparison, observations


def main() -> int:
    args = parse_args()

    comparison_path = args.output_dir / "comparison.csv"
    observations_path = args.output_dir / "observations.csv"

    for path in (comparison_path, observations_path):
        if same_path(args.input, path):
            print(f"Błąd: wynik nie może nadpisać pliku wejściowego: {path}", file=sys.stderr)
            return 1

    if not args.input.is_file():
        print(f"Błąd: nie znaleziono pliku wejściowego: {args.input}", file=sys.stderr)
        return 1

    df = pd.read_csv(args.input, encoding="utf-8-sig", low_memory=False)
    try:
        validate_input(df, args.test_size)
    except ValueError as error:
        print(f"Błąd: {error}", file=sys.stderr)
        return 1

    split = split_label(args.test_size)
    train, test = train_test_split(df, test_size=args.test_size, random_state=args.seed, shuffle=True)

    if len(test) < MIN_TEST_ROWS:
        print(f"Błąd: zbiór testowy ma {len(test)} wiersze, wymagane co najmniej {MIN_TEST_ROWS}", file=sys.stderr)
        return 1

    print(f"Plik wejściowy:   {args.input}")
    print(f"Katalog wynikowy: {args.output_dir}")
    print(f"Podział: {split} (test_size={args.test_size}), ziarno {args.seed}, alpha={args.alpha}")
    print(f"  train: {len(train)}, test: {len(test)}")
    print()

    self_check_metrics()

    comparison, observations = run(df, args, split, train, test)

    print("Wyniki na teście:")
    for _, row in comparison.iterrows():
        print(
            f"  {row['method']:<8} MAE {row['mae_pln']:>10.2f} PLN  "
            f"RMSE {row['rmse_pln']:>10.2f} PLN  R2 {row['r2']:>7.4f}  MAPE {row['mape_pct']:>6.2f} %"
        )

    baseline_mae = float(comparison.loc[comparison["method"] == "baseline", "mae_pln"].iloc[0])
    model_mae = float(comparison.loc[comparison["method"] == "ridge", "mae_pln"].iloc[0])
    difference = model_mae - baseline_mae
    relative = difference / baseline_mae * 100 if baseline_mae else float("nan")
    print(f"  różnica MAE (model - baseline): {difference:+.2f} PLN ({relative:+.2f} %)")
    print()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    comparison.round({"mae_pln": 2, "rmse_pln": 2, "r2": 4, "mape_pct": 2}).to_csv(
        comparison_path, index=False, encoding="utf-8-sig"
    )
    observations.round(2).to_csv(observations_path, index=False, encoding="utf-8-sig")

    print("Zapisano:")
    print(f"  {comparison_path} ({len(comparison)} wiersze)")
    print(f"  {observations_path} ({len(observations)} wierszy)")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
