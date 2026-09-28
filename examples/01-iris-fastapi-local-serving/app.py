"""FastAPI inference service for the trained Iris classifier.

This module represents the *online serving stage* of the ML lifecycle.
Training is intentionally absent: the notebook creates versioned artifacts
before deployment, and this application loads them once during startup.
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field

BASE_DIR = Path(__file__).resolve().parent
ARTIFACT_DIR = BASE_DIR / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "iris_model.joblib"
METADATA_PATH = ARTIFACT_DIR / "model_metadata.json"
METRICS_PATH = ARTIFACT_DIR / "metrics.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("iris-api")


class IrisFeatures(BaseModel):
    """Validated request contract for one Iris flower."""

    model_config = ConfigDict(extra="forbid")

    sepal_length_cm: float = Field(..., gt=0, le=20, description="Sepal length in centimetres", examples=[5.1])
    sepal_width_cm: float = Field(..., gt=0, le=20, description="Sepal width in centimetres", examples=[3.5])
    petal_length_cm: float = Field(..., gt=0, le=20, description="Petal length in centimetres", examples=[1.4])
    petal_width_cm: float = Field(..., gt=0, le=20, description="Petal width in centimetres", examples=[0.2])


class PredictionResponse(BaseModel):
    prediction: str
    class_id: int
    probabilities: dict[str, float]
    model_version: str


class BatchPredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    items: list[IrisFeatures] = Field(..., min_length=1, max_length=100)


class BatchPredictionResponse(BaseModel):
    predictions: list[PredictionResponse]
    count: int


class LivenessResponse(BaseModel):
    status: str


class ReadinessResponse(BaseModel):
    status: str
    model_loaded: bool
    model_name: str
    model_version: str


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _assert_artifacts_exist() -> None:
    missing = [str(path) for path in (MODEL_PATH, METADATA_PATH, METRICS_PATH) if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Required model artifacts are missing. Execute "
            "notebooks/01_train_iris_model.ipynb first. Missing: " + ", ".join(missing)
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load immutable model artifacts once when the application starts."""

    _assert_artifacts_exist()
    logger.info("Loading model artifact from %s", MODEL_PATH)

    app.state.model = joblib.load(MODEL_PATH)
    app.state.metadata = _load_json(METADATA_PATH)
    app.state.metrics = _load_json(METRICS_PATH)

    logger.info(
        "Model ready: name=%s version=%s",
        app.state.metadata["model_name"],
        app.state.metadata["model_version"],
    )

    yield

    logger.info("Shutting down Iris API")


app = FastAPI(
    title="Iris ML Model Serving API",
    summary="Professional-course example of serving a trained scikit-learn model.",
    description=(
        "The model is trained offline in a Jupyter notebook and serialized as a deployment artifact. "
        "This application performs inference only. Explore the contract interactively through /docs."
    ),
    version="1.1.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def request_context(request: Request, call_next):
    """Attach a request ID and simple processing-time header for observability."""

    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    started = time.perf_counter()

    response: Response = await call_next(request)

    duration_ms = (time.perf_counter() - started) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time-Ms"] = f"{duration_ms:.3f}"

    logger.info(
        "request_id=%s method=%s path=%s status=%s duration_ms=%.3f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


def _predict_one(request: Request, features: IrisFeatures) -> PredictionResponse:
    metadata = request.app.state.metadata
    model = request.app.state.model

    feature_names: list[str] = metadata["feature_names"]
    payload = features.model_dump()
    frame = pd.DataFrame([[payload[name] for name in feature_names]], columns=feature_names)

    class_id = int(model.predict(frame)[0])
    probability_values = model.predict_proba(frame)[0]
    class_names: list[str] = metadata["class_names"]

    probabilities = {
        class_name: round(float(probability), 6)
        for class_name, probability in zip(class_names, probability_values, strict=True)
    }

    return PredictionResponse(
        prediction=class_names[class_id],
        class_id=class_id,
        probabilities=probabilities,
        model_version=metadata["model_version"],
    )


@app.get("/", tags=["service"])
def root(request: Request) -> dict[str, str]:
    metadata = request.app.state.metadata
    return {
        "service": "Iris ML Model Serving API",
        "model": metadata["model_name"],
        "model_version": metadata["model_version"],
        "swagger": "/docs",
        "openapi": "/openapi.json",
        "liveness": "/health/live",
        "readiness": "/health/ready",
    }


@app.get("/health", response_model=ReadinessResponse, include_in_schema=False)
def health_alias(request: Request) -> ReadinessResponse:
    """Backwards-compatible alias for readiness."""
    return ready(request)


@app.get("/health/live", response_model=LivenessResponse, tags=["health"])
def live() -> LivenessResponse:
    """Liveness means the web application process can answer a request."""
    return LivenessResponse(status="alive")


@app.get("/health/ready", response_model=ReadinessResponse, tags=["health"])
def ready(request: Request) -> ReadinessResponse:
    """Readiness means the model has loaded and this instance can serve traffic."""

    if not hasattr(request.app.state, "model"):
        raise HTTPException(status_code=503, detail="Model is not loaded")

    metadata = request.app.state.metadata
    return ReadinessResponse(
        status="ready",
        model_loaded=True,
        model_name=metadata["model_name"],
        model_version=metadata["model_version"],
    )


@app.get("/model-info", tags=["model"])
def model_info(request: Request) -> dict[str, Any]:
    return {
        "metadata": request.app.state.metadata,
        "evaluation_metrics": request.app.state.metrics,
    }


@app.post("/predict", response_model=PredictionResponse, tags=["inference"])
def predict(features: IrisFeatures, request: Request) -> PredictionResponse:
    """Predict the Iris class for one validated feature vector."""
    return _predict_one(request, features)


@app.post("/predict/batch", response_model=BatchPredictionResponse, tags=["inference"])
def predict_batch(payload: BatchPredictionRequest, request: Request) -> BatchPredictionResponse:
    """Predict up to 100 feature vectors in a single request."""
    predictions = [_predict_one(request, item) for item in payload.items]
    return BatchPredictionResponse(predictions=predictions, count=len(predictions))
