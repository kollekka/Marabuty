"""HTTP request and response schemas for price estimates."""

from __future__ import annotations

import math
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictInt,
    StrictStr,
    field_validator,
    model_validator,
)


Gearbox = Literal["Manualna", "Automatyczna", "Półautomatyczna"]
Comparison = Literal["below_estimate", "around_estimate", "above_estimate"]


class PredictRequest(BaseModel):
    """Vehicle details and asking price for one used-car valuation."""

    model_config = ConfigDict(extra="forbid")

    make: StrictStr = Field(min_length=1, max_length=100)
    model: StrictStr = Field(min_length=1, max_length=100)
    year: StrictInt = Field(ge=1950, le=2027)
    mileage_km: StrictInt = Field(ge=0, le=2_000_000)
    engine_cc: StrictInt | None = Field(default=None, ge=500, le=8_000)
    engine_power_km: StrictInt | None = Field(default=None, ge=20, le=2_000)
    fuel_type: StrictStr | None = Field(default=None, min_length=1, max_length=100)
    gearbox: Gearbox | None = None
    transmission: StrictStr | None = Field(default=None, min_length=1, max_length=100)
    body_type: StrictStr | None = Field(default=None, min_length=1, max_length=100)
    region: StrictStr | None = Field(default=None, min_length=1, max_length=100)
    asking_price_pln: float = Field(ge=1_000, le=5_000_000, allow_inf_nan=False)

    @field_validator(
        "make",
        "model",
        "fuel_type",
        "transmission",
        "body_type",
        "region",
        mode="before",
    )
    @classmethod
    def strip_text_fields(cls, value: object) -> object:
        if value is None:
            return None
        if not isinstance(value, str):
            return value
        value = value.strip()
        if not value:
            raise ValueError("pole tekstowe nie może być puste")
        return value

    @field_validator("asking_price_pln", mode="before")
    @classmethod
    def validate_asking_price_number(cls, value: object) -> object:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("cena ofertowa musi być liczbą JSON")
        if not math.isfinite(float(value)):
            raise ValueError("cena ofertowa musi być skończona")
        return float(value)


class PredictionInterval(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lower: float = Field(gt=0, allow_inf_nan=False)
    upper: float = Field(gt=0, allow_inf_nan=False)


class PredictResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    estimated_price_pln: float = Field(gt=0, allow_inf_nan=False)
    prediction_interval_pln: PredictionInterval
    asking_price_pln: float = Field(ge=1_000, le=5_000_000, allow_inf_nan=False)
    comparison: Comparison
    currency: Literal["PLN"] = "PLN"
    method: StrictStr = Field(min_length=1)
    model_version: StrictStr = Field(min_length=1)
    data_version: StrictStr = Field(min_length=1)

    @model_validator(mode="after")
    def interval_contains_estimate(self) -> PredictResponse:
        interval = self.prediction_interval_pln
        if interval.lower > self.estimated_price_pln or self.estimated_price_pln > interval.upper:
            raise ValueError("przedział musi zawierać prognozę punktową")
        return self
