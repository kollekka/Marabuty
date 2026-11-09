"""Loading and invoking the trained model bundle.

The model trainer is a separate project task. The expected joblib object is a
mapping with ``pipeline`` and ``interval_calibrator`` entries. The pipeline
predicts ``log1p(price_pln)``; the calibrator exposes
``predict_interval(point_prediction_pln, feature_frame) -> (lower, upper)``
and returns finite PLN bounds containing the point prediction.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

import joblib
import pandas as pd


MODEL_FEATURES = [
    "year",
    "mileage_km",
    "engine_cc",
    "engine_power_km",
    "make",
    "model",
    "fuel_type",
    "gearbox",
    "transmission",
    "body_type",
    "new_used",
    "region",
]


class ModelNotReady(Exception):
    """The model artifact or its interval calibrator is unavailable."""


class PredictionFailure(Exception):
    """The model returned an invalid prediction or failed during inference."""


class IntervalCalibrator(Protocol):
    def predict_interval(
        self, point_prediction_pln: float, feature_frame: pd.DataFrame
    ) -> tuple[float, float]: ...


@dataclass(frozen=True)
class RuntimePrediction:
    estimated_price_pln: float
    lower_pln: float
    upper_pln: float
    method: str
    model_version: str
    data_version: str


class PredictionRuntime:
    """One loaded pipeline plus its calibrated prediction interval."""

    def __init__(
        self,
        pipeline: Any,
        interval_calibrator: IntervalCalibrator,
        *,
        method: str,
        model_version: str,
        data_version: str,
    ) -> None:
        self.pipeline = pipeline
        self.interval_calibrator = interval_calibrator
        self.method = method
        self.model_version = model_version
        self.data_version = data_version

    @classmethod
    def from_files(cls, model_dir: Path) -> PredictionRuntime:
        model_path = model_dir / "price-ridge.joblib"
        manifest_path = model_dir / "manifest.json"
        if not model_path.is_file() or not manifest_path.is_file():
            raise ModelNotReady("brak models/price-ridge.joblib lub models/manifest.json")

        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            bundle = joblib.load(model_path)
        except Exception as error:
            raise ModelNotReady("nie można wczytać artefaktu modelu i manifestu") from error

        required_manifest_fields = {
            "model_version",
            "data_version",
            "method",
            "target_transform",
            "features",
            "scope",
            "interval_method",
            "interval_coverage",
        }
        if not isinstance(manifest, dict) or not required_manifest_fields.issubset(manifest):
            raise ModelNotReady("manifest nie zawiera wymaganych metadanych")
        if manifest["scope"] != "Używane" or manifest["target_transform"] != "log1p":
            raise ModelNotReady("model nie odpowiada zakresowi Używane/log1p")
        if manifest["features"] != MODEL_FEATURES:
            raise ModelNotReady("lista lub kolejność cech modelu nie zgadza się z API")
        string_fields = ("model_version", "data_version", "method", "interval_method")
        if not all(isinstance(manifest[field], str) and manifest[field] for field in string_fields):
            raise ModelNotReady("manifest zawiera puste identyfikatory wersji lub metody")
        coverage = manifest["interval_coverage"]
        if isinstance(coverage, bool) or not isinstance(coverage, (int, float)) or not 0 < coverage < 1:
            raise ModelNotReady("interval_coverage w manifeście musi być z przedziału (0, 1)")
        if not isinstance(bundle, dict):
            raise ModelNotReady("artefakt joblib musi być mapą pipeline/calibrator")

        pipeline = bundle.get("pipeline")
        calibrator = bundle.get("interval_calibrator")
        if not callable(getattr(pipeline, "predict", None)):
            raise ModelNotReady("artefakt nie zawiera pipeline'u z metodą predict")
        if not callable(getattr(calibrator, "predict_interval", None)):
            raise ModelNotReady("artefakt nie zawiera skalibrowanego przedziału")

        return cls(
            pipeline,
            calibrator,
            method=manifest["method"],
            model_version=manifest["model_version"],
            data_version=manifest["data_version"],
        )

    def predict(self, vehicle_features: dict[str, object]) -> RuntimePrediction:
        feature_values = {**vehicle_features, "new_used": "Używane"}
        feature_frame = pd.DataFrame([feature_values], columns=MODEL_FEATURES)

        try:
            log_prediction = self.pipeline.predict(feature_frame)
            if len(log_prediction) != 1:
                raise PredictionFailure("model musi zwrócić dokładnie jedną prognozę")
            estimated_price = math.expm1(float(log_prediction[0]))
            bounds = self.interval_calibrator.predict_interval(estimated_price, feature_frame)
            if len(bounds) != 2:
                raise PredictionFailure("kalibrator musi zwrócić dwie granice przedziału")
            lower, upper = (float(bounds[0]), float(bounds[1]))
        except PredictionFailure:
            raise
        except Exception as error:
            raise PredictionFailure("błąd podczas obliczania prognozy") from error

        if not all(math.isfinite(value) and value > 0 for value in (estimated_price, lower, upper)):
            raise PredictionFailure("prognoza i granice muszą być skończonymi dodatnimi liczbami")
        if lower > estimated_price or estimated_price > upper:
            raise PredictionFailure("przedział musi zawierać prognozę punktową")

        return RuntimePrediction(
            estimated_price_pln=estimated_price,
            lower_pln=lower,
            upper_pln=upper,
            method=self.method,
            model_version=self.model_version,
            data_version=self.data_version,
        )
