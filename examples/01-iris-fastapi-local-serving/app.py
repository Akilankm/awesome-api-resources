"""FastAPI inference service for the trained Iris classifier.

Training is intentionally NOT performed in this file. The notebook creates
versioned artifacts offline; this application only loads those artifacts and
serves predictions over HTTP.
"""

from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

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

    sepal_length_cm: float = Field(..., gt=0, description="Sepal length in centimetres", examples=[5.1])
    sepal_width_cm: float = Field(..., gt=0, description="Sepal width in centimetres", examples=[3.5])
    petal_length_cm: float = Field(..., gt=0, description="Petal length in centimetres", examples=[1.4])
    petal_width_cm: float = Field(..., gt=0, description="Petal width in centimetres", examples=[0.2])


class PredictionResponse(BaseModel):
    prediction: str
    class_id: int
    probabilities: dict[str, float]
    model_version: str


class BatchPredictionRequest(BaseModel):
    items: list[IrisFeatures] = Field(..., min_length=1, max_length=100)


class BatchPredictionResponse(BaseModel):
    predictions: list[PredictionResponse]
    count: int


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
    """Load model artifacts once at application startup."""

    _assert_artifacts_exist()
    logger.info("Loading model from %s", MODEL_PATH)

    app.state.model = joblib.load(MODEL_PATH)
    app.state.metadata = _load_json(METADATA_PATH)
    app.state.metrics = _load_json(METRICS_PATH)

    logger.info(
        "Model loaded: name=%s version=%s",
        app.state.metadata["model_name"],
        app.state.metadata["model_version"],
    )

    yield
    logger.info("Shutting down Iris API")


app = FastAPI(
    title="Iris ML Model Serving API",
    summary="A deployment-oriented example of serving a trained scikit-learn model.",
    description=(
        "The model is trained offline in a Jupyter notebook and serialized as an artifact. "
        "This FastAPI application performs inference only. Use /docs for interactive Swagger UI."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


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
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["service"])
def health(request: Request) -> dict[str, Any]:
    model_loaded = hasattr(request.app.state, "model")
    if not model_loaded:
        raise HTTPException(status_code=503, detail="Model is not loaded")

    return {
        "status": "ok",
        "model_loaded": True,
        "model_name": request.app.state.metadata["model_name"],
        "model_version": request.app.state.metadata["model_version"],
    }


@app.get("/model-info", tags=["model"])
def model_info(request: Request) -> dict[str, Any]:
    return {
        "metadata": request.app.state.metadata,
        "evaluation_metrics": request.app.state.metrics,
    }


@app.post("/predict", response_model=PredictionResponse, tags=["inference"])
def predict(features: IrisFeatures, request: Request) -> PredictionResponse:
    return _predict_one(request, features)


@app.post("/predict/batch", response_model=BatchPredictionResponse, tags=["inference"])
def predict_batch(payload: BatchPredictionRequest, request: Request) -> BatchPredictionResponse:
    predictions = [_predict_one(request, item) for item in payload.items]
    return BatchPredictionResponse(predictions=predictions, count=len(predictions))
