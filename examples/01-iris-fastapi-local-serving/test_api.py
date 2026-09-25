"""Smoke tests for the local FastAPI inference service."""

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
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["model_loaded"] is True

        model_info = client.get("/model-info")
        assert model_info.status_code == 200
        assert model_info.json()["metadata"]["model_name"] == "iris-logistic-regression"

        prediction = client.post("/predict", json=VALID_SAMPLE)
        assert prediction.status_code == 200
        body = prediction.json()
        assert body["prediction"] == "setosa"
        assert body["class_id"] == 0
        assert abs(sum(body["probabilities"].values()) - 1.0) < 1e-5

        batch = client.post("/predict/batch", json={"items": [VALID_SAMPLE, VALID_SAMPLE]})
        assert batch.status_code == 200
        assert batch.json()["count"] == 2

        invalid = client.post("/predict", json={**VALID_SAMPLE, "sepal_length_cm": -1})
        assert invalid.status_code == 422


if __name__ == "__main__":
    test_service_contract()
    print("All FastAPI smoke tests passed.")
