from __future__ import annotations

import math

import pytest

from app.runtime import MODEL_FEATURES, PredictionFailure, PredictionRuntime


class FakePipeline:
    def __init__(self, log_prediction: float) -> None:
        self.log_prediction = log_prediction
        self.received_frame = None

    def predict(self, feature_frame):
        self.received_frame = feature_frame
        return [self.log_prediction]


class FakeCalibrator:
    def predict_interval(self, point_prediction_pln: float, feature_frame):
        return (point_prediction_pln - 5_500, point_prediction_pln + 6_500)


def test_runtime_inverts_log_target_and_adds_used_car_feature() -> None:
    pipeline = FakePipeline(math.log1p(62_500))
    runtime = PredictionRuntime(
        pipeline,
        FakeCalibrator(),
        method="ridge_log_linear",
        model_version="ridge-used-test",
        data_version="test-data-v1",
    )

    prediction = runtime.predict(
        {
            "make": "Toyota",
            "model": "Corolla",
            "year": 2020,
            "mileage_km": 65_000,
            "engine_cc": 1_798,
            "engine_power_km": 122,
            "fuel_type": "Hybryda",
            "gearbox": "Automatyczna",
            "transmission": "Napęd na przednie koła",
            "body_type": "Hatchback",
            "region": "Mazowieckie",
        }
    )

    assert prediction.estimated_price_pln == pytest.approx(62_500)
    assert prediction.lower_pln == pytest.approx(57_000)
    assert prediction.upper_pln == pytest.approx(69_000)
    assert list(pipeline.received_frame.columns) == MODEL_FEATURES
    assert pipeline.received_frame.loc[0, "new_used"] == "Używane"


def test_runtime_rejects_interval_that_does_not_contain_prediction() -> None:
    class BadCalibrator:
        def predict_interval(self, point_prediction_pln: float, feature_frame):
            return (70_000, 80_000)

    runtime = PredictionRuntime(
        FakePipeline(math.log1p(62_500)),
        BadCalibrator(),
        method="ridge_log_linear",
        model_version="ridge-used-test",
        data_version="test-data-v1",
    )

    with pytest.raises(PredictionFailure, match="przedział musi zawierać"):
        runtime.predict({"make": "Toyota", "model": "Corolla"})
