"""Contract tests for the local FastAPI inference service."""

from fastapi.testclient import TestClient

from app import app

VALID_SAMPLE = {
    "sepal_length_cm": 5.1,
    "sepal_width_cm": 3.5,
    "petal_length_cm": 1.4,
    "petal_width_cm": 0.2,
}


def test_service_contract() -> None:
    with TestClient(app) as client:
        root = client.get("/")
        assert root.status_code == 200
        assert root.json()["swagger"] == "/docs"

        live = client.get("/health/live")
        assert live.status_code == 200
        assert live.json() == {"status": "alive"}

        ready = client.get("/health/ready")
        assert ready.status_code == 200
        assert ready.json()["model_loaded"] is True
        assert ready.json()["status"] == "ready"

        model_info = client.get("/model-info")
        assert model_info.status_code == 200
        assert model_info.json()["metadata"]["model_name"] == "iris-logistic-regression"
        assert "accuracy" in model_info.json()["evaluation_metrics"]

        prediction = client.post("/predict", json=VALID_SAMPLE)
        assert prediction.status_code == 200
        body = prediction.json()
        assert body["prediction"] == "setosa"
        assert body["class_id"] == 0
        assert abs(sum(body["probabilities"].values()) - 1.0) < 1e-5
        assert prediction.headers["X-Request-ID"]
        assert float(prediction.headers["X-Process-Time-Ms"]) >= 0

        batch = client.post("/predict/batch", json={"items": [VALID_SAMPLE, VALID_SAMPLE]})
        assert batch.status_code == 200
        assert batch.json()["count"] == 2

        invalid_negative = client.post("/predict", json={**VALID_SAMPLE, "sepal_length_cm": -1})
        assert invalid_negative.status_code == 422

        invalid_missing = client.post(
            "/predict",
            json={k: v for k, v in VALID_SAMPLE.items() if k != "petal_width_cm"},
        )
        assert invalid_missing.status_code == 422

        invalid_extra = client.post("/predict", json={**VALID_SAMPLE, "unexpected": 123})
        assert invalid_extra.status_code == 422

        too_large_batch = client.post("/predict/batch", json={"items": [VALID_SAMPLE] * 101})
        assert too_large_batch.status_code == 422

        openapi = client.get("/openapi.json")
        assert openapi.status_code == 200
        schema = openapi.json()
        assert "/predict" in schema["paths"]
        assert "/health/live" in schema["paths"]
        assert "/health/ready" in schema["paths"]


if __name__ == "__main__":
    test_service_contract()
    print("All FastAPI contract tests passed.")
