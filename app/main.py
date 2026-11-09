"""FastAPI application for single used-car price estimates."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.runtime import ModelNotReady, PredictionFailure, PredictionRuntime
from app.schemas import PredictRequest, PredictResponse, PredictionInterval

logger = logging.getLogger(__name__)


class ApiError(Exception):
    def __init__(self, status_code: int, error: str, detail: str) -> None:
        self.status_code = status_code
        self.error = error
        self.detail = detail


def create_app(model_dir: Path | None = None) -> FastAPI:
    api = FastAPI(title="Wycena używanych samochodów", version="0.1.0")
    api.state.model_dir = model_dir or Path(os.environ.get("MODEL_DIR", "models"))
    api.state.prediction_runtime = None

    @api.exception_handler(RequestValidationError)
    async def request_validation_error_handler(
        request: Request, error: RequestValidationError
    ) -> JSONResponse:
        errors = error.errors()
        if any(item.get("type") == "json_invalid" for item in errors):
            return JSONResponse(
                status_code=400,
                content={
                    "error": "invalid_json",
                    "detail": "Treść żądania nie jest poprawnym JSON-em.",
                },
            )

        details = [
            {
                "field": ".".join(str(part) for part in item.get("loc", ()) if part != "body"),
                "message": item.get("msg", "niepoprawna wartość"),
            }
            for item in errors
        ]
        return JSONResponse(
            status_code=422,
            content={"error": "invalid_vehicle_input", "detail": details},
        )

    @api.exception_handler(ApiError)
    async def api_error_handler(request: Request, error: ApiError) -> JSONResponse:
        return JSONResponse(
            status_code=error.status_code,
            content={"error": error.error, "detail": error.detail},
        )

    def get_prediction_runtime(request: Request) -> PredictionRuntime:
        runtime = request.app.state.prediction_runtime
        if runtime is not None:
            return runtime
        try:
            runtime = PredictionRuntime.from_files(request.app.state.model_dir)
        except ModelNotReady as error:
            raise ApiError(503, "model_not_ready", str(error)) from error
        request.app.state.prediction_runtime = runtime
        return runtime

    @api.post("/predict", response_model=PredictResponse)
    def predict_price(
        payload: PredictRequest,
        runtime: PredictionRuntime = Depends(get_prediction_runtime),
    ) -> PredictResponse:
        vehicle_features: dict[str, Any] = payload.model_dump(exclude={"asking_price_pln"})
        vehicle_features["new_used"] = "Używane"
        try:
            prediction = runtime.predict(vehicle_features)
        except PredictionFailure as error:
            logger.exception("Model prediction failed")
            raise ApiError(500, "prediction_failed", str(error)) from error
        except Exception as error:
            logger.exception("Unexpected prediction error")
            raise ApiError(500, "prediction_failed", "Nie udało się obliczyć wyceny.") from error

        asking_price = payload.asking_price_pln
        if asking_price < prediction.lower_pln:
            comparison = "below_estimate"
        elif asking_price > prediction.upper_pln:
            comparison = "above_estimate"
        else:
            comparison = "around_estimate"

        try:
            return PredictResponse(
                estimated_price_pln=prediction.estimated_price_pln,
                prediction_interval_pln=PredictionInterval(
                    lower=prediction.lower_pln,
                    upper=prediction.upper_pln,
                ),
                asking_price_pln=asking_price,
                comparison=comparison,
                method=prediction.method,
                model_version=prediction.model_version,
                data_version=prediction.data_version,
            )
        except Exception as error:
            logger.exception("Model returned a response outside the API contract")
            raise ApiError(
                500,
                "prediction_failed",
                "Model zwrócił wynik poza kontraktem API.",
            ) from error

    # Expose the dependency so tests and future application wiring can provide a runtime.
    api.state.get_prediction_runtime = get_prediction_runtime
    return api


app = create_app()
