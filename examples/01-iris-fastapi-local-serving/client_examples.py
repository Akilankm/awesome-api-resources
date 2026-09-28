"""HTTP client example for the locally running Iris service."""

from __future__ import annotations

import json
import httpx

BASE_URL = "http://127.0.0.1:8000"

sample = {
    "sepal_length_cm": 5.1,
    "sepal_width_cm": 3.5,
    "petal_length_cm": 1.4,
    "petal_width_cm": 0.2,
}


def main() -> None:
    with httpx.Client(base_url=BASE_URL, timeout=5.0) as client:
        ready = client.get("/health/ready")
        ready.raise_for_status()
        print("READINESS")
        print(json.dumps(ready.json(), indent=2))

        prediction = client.post("/predict", json=sample)
        prediction.raise_for_status()
        print("\nPREDICTION")
        print(json.dumps(prediction.json(), indent=2))


if __name__ == "__main__":
    main()
