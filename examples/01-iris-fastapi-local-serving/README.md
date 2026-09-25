# Iris ML Model Serving with FastAPI — Local Deployment Foundation

This example teaches the first deployment boundary every ML engineer should understand:

> **Train offline → create immutable artifacts → load artifacts in an inference service → expose the model through HTTP.**

The notebook owns training and artifact creation. `app.py` owns only API startup, validation, inference, and responses.

## Where this fits in cloud and deployment

```text
OFFLINE / BUILD-TIME                         ONLINE / RUN-TIME
────────────────────                         ──────────────────
Dataset                                      Client
   │                                            │ HTTP JSON
   ▼                                            ▼
Training notebook                         FastAPI service
   │                                            │
   ├── preprocessing                            ▼
   ├── model training                      model artifact
   └── evaluation                               │
   │                                            ▼
   ▼                                        prediction
artifacts/                                      │
   ├── iris_model.joblib                        ▼
   ├── model_metadata.json                 JSON response
   └── metrics.json
```

The same boundary remains when the service later moves from a laptop to Docker, a VM, Kubernetes, Azure, AWS, GCP, or a managed serving platform.

## Project structure

```text
01-iris-fastapi-local-serving/
├── environment.yml
├── notebooks/
│   └── 01_train_iris_model.ipynb
├── artifacts/
│   ├── iris_model.joblib
│   ├── model_metadata.json
│   └── metrics.json
├── app.py
├── test_api.py
└── README.md
```

## 1. Create the Conda environment

```bash
conda env create -f environment.yml
conda activate awesome-api-resources
```

If the environment already exists:

```bash
conda env update -f environment.yml --prune
conda activate awesome-api-resources
```

## 2. Rebuild the model artifacts

```bash
jupyter lab
```

Open and execute:

```text
notebooks/01_train_iris_model.ipynb
```

The notebook is the **build stage**. It loads Iris, defines the API feature contract, splits data, trains a scikit-learn `Pipeline`, evaluates it, writes artifacts, and reloads the serialized model to prove the deployment artifact works.

## 3. Test the API before serving

```bash
python test_api.py
# or
pytest -q test_api.py
```

The smoke test verifies model startup, `/health`, `/model-info`, single prediction, batch prediction, and HTTP 422 validation for invalid input.

## 4. Serve locally

```bash
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

Open:

- API root: `http://127.0.0.1:8000/`
- Health: `http://127.0.0.1:8000/health`
- Model info: `http://127.0.0.1:8000/model-info`
- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`

## 5. Call the model

```bash
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "sepal_length_cm": 5.1,
    "sepal_width_cm": 3.5,
    "petal_length_cm": 1.4,
    "petal_width_cm": 0.2
  }'
```

Expected result from the committed artifact:

```json
{
  "prediction": "setosa",
  "class_id": 0,
  "probabilities": {
    "setosa": 0.980813,
    "versicolor": 0.019187,
    "virginica": 0.0
  },
  "model_version": "1.0.0"
}
```

## Why use a scikit-learn Pipeline?

```text
raw request features
       ↓
StandardScaler
       ↓
LogisticRegression
       ↓
prediction
```

The serialized artifact contains preprocessing and the estimator together. This prevents **training-serving skew**.

## Why does app.py never train?

| Build / training stage | Serving / runtime stage |
|---|---|
| Reads training data | Receives API requests |
| Fits parameters | Uses fitted parameters |
| Evaluates model | Produces predictions |
| Writes artifacts | Reads artifacts |
| Can be compute-heavy | Must start and respond predictably |

A production service should not retrain whenever its web server restarts.

## Deployment mental model

```text
Notebook / training job
        ↓
Model artifact
        ↓
FastAPI application
        ↓
Container image
        ↓
Container registry
        ↓
Cloud runtime / Kubernetes / managed service
        ↓
Load balancer + monitoring + autoscaling
```

The next deployment stage should containerize this same tested API rather than rewrite the model logic.
