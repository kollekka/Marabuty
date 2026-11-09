from __future__ import annotations

from fastapi.testclient import TestClient
import pytest

from app.main import create_app
from app.runtime import PredictionFailure, RuntimePrediction


VALID_REQUEST = {
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
    "asking_price_pln": 64_000,
}


class FakeRuntime:
    def __init__(self, prediction: RuntimePrediction | None = None, error: Exception | None = None):
        self.prediction = prediction or RuntimePrediction(
            estimated_price_pln=62_500.0,
            lower_pln=57_000.0,
            upper_pln=69_000.0,
            method="ridge_log_linear",
            model_version="ridge-used-test",
            data_version="test-data-v1",
        )
        self.error = error
        self.received_features: dict[str, object] | None = None

    def predict(self, vehicle_features: dict[str, object]) -> RuntimePrediction:
        self.received_features = vehicle_features
        if self.error is not None:
            raise self.error
        return self.prediction


def client_with_runtime(runtime: FakeRuntime) -> TestClient:
    api = create_app()
    api.dependency_overrides[api.state.get_prediction_runtime] = lambda: runtime
    return TestClient(api)


@pytest.mark.parametrize(
    ("asking_price", "expected_comparison"),
    [
        (56_999, "below_estimate"),
        (57_000, "around_estimate"),
        (69_000, "around_estimate"),
        (69_001, "above_estimate"),
    ],
)
def test_predict_returns_estimate_interval_and_offer_comparison(
    asking_price: int, expected_comparison: str
) -> None:
    runtime = FakeRuntime()
    client = client_with_runtime(runtime)
    request = {**VALID_REQUEST, "asking_price_pln": asking_price}

    response = client.post("/predict", json=request)

    assert response.status_code == 200
    assert response.json() == {
        "estimated_price_pln": 62_500.0,
        "prediction_interval_pln": {"lower": 57_000.0, "upper": 69_000.0},
        "asking_price_pln": float(asking_price),
        "comparison": expected_comparison,
        "currency": "PLN",
        "method": "ridge_log_linear",
        "model_version": "ridge-used-test",
        "data_version": "test-data-v1",
    }
    assert runtime.received_features is not None
    assert runtime.received_features["new_used"] == "Używane"
    assert "asking_price_pln" not in runtime.received_features


def test_invalid_json_returns_400_without_price() -> None:
    client = client_with_runtime(FakeRuntime())

    response = client.post(
        "/predict",
        content='{"make":',
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 400
    assert response.json()["error"] == "invalid_json"
    assert "estimated_price_pln" not in response.json()


def test_missing_required_field_returns_422_without_price() -> None:
    client = client_with_runtime(FakeRuntime())
    request = dict(VALID_REQUEST)
    del request["model"]

    response = client.post("/predict", json=request)

    assert response.status_code == 422
    assert response.json()["error"] == "invalid_vehicle_input"
    assert "estimated_price_pln" not in response.json()


@pytest.mark.parametrize(
    ("changes", "expected_error"),
    [
        ({"year": 1949}, "invalid_vehicle_input"),
        ({"mileage_km": -1}, "invalid_vehicle_input"),
        ({"asking_price_pln": 999}, "invalid_vehicle_input"),
        ({"new_used": "Nowość"}, "invalid_vehicle_input"),
        ({"make": "   "}, "invalid_vehicle_input"),
    ],
)
def test_invalid_vehicle_input_returns_422_without_price(
    changes: dict[str, object], expected_error: str
) -> None:
    client = client_with_runtime(FakeRuntime())

    response = client.post("/predict", json={**VALID_REQUEST, **changes})

    assert response.status_code == 422
    assert response.json()["error"] == expected_error
    assert "estimated_price_pln" not in response.json()


def test_valid_request_without_model_returns_503_without_price(tmp_path) -> None:
    client = TestClient(create_app(model_dir=tmp_path))

    response = client.post("/predict", json=VALID_REQUEST)

    assert response.status_code == 503
    assert response.json()["error"] == "model_not_ready"
    assert "estimated_price_pln" not in response.json()


def test_prediction_failure_returns_500_without_price() -> None:
    client = client_with_runtime(FakeRuntime(error=PredictionFailure("invalid output")))

    response = client.post("/predict", json=VALID_REQUEST)

    assert response.status_code == 500
    assert response.json()["error"] == "prediction_failed"
    assert "estimated_price_pln" not in response.json()


def test_invalid_prediction_interval_returns_500_without_price() -> None:
    invalid_runtime = FakeRuntime(
        prediction=RuntimePrediction(
            estimated_price_pln=62_500.0,
            lower_pln=70_000.0,
            upper_pln=80_000.0,
            method="ridge_log_linear",
            model_version="ridge-used-test",
            data_version="test-data-v1",
        )
    )
    client = client_with_runtime(invalid_runtime)

    response = client.post("/predict", json=VALID_REQUEST)

    assert response.status_code == 500
    assert response.json()["error"] == "prediction_failed"
    assert "estimated_price_pln" not in response.json()
