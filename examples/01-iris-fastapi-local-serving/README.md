# Module 01 — Serving an ML Model Locally with FastAPI

> **Professional course lab:** train a model offline, package deployable artifacts, expose inference through a typed HTTP API, test the service, and connect every local concept to its production/cloud equivalent.

## What you will learn

After completing this module, you should be able to explain—not just execute—the following:

- why training and serving are separate lifecycle stages;
- what a model artifact is and why metadata belongs beside it;
- how a JSON request becomes a model prediction;
- why feature order and preprocessing consistency matter;
- how Pydantic validates an API contract;
- how FastAPI, Uvicorn, OpenAPI, and Swagger relate;
- the difference between liveness and readiness;
- why a model should load once at application startup;
- how automated API tests protect the serving contract;
- which parts stay unchanged when the service later moves to Docker and cloud infrastructure.

## Prerequisites

You should already be comfortable with basic Python, pandas/scikit-learn, and train/test split. You do **not** need prior FastAPI, Docker, Kubernetes, or cloud experience.

## 1. Architecture first

```text
                     OFFLINE / BUILD TIME
                          Iris dataset
                               │
                               ▼
                      Jupyter notebook
                               │
              preprocessing + training + evaluation
                               │
                               ▼
                         artifacts/
                  ┌────────────┼────────────┐
                  ▼            ▼            ▼
             model.joblib   metadata      metrics
                  │
                  │ lifecycle boundary
                  ▼
                     ONLINE / RUN TIME
 Client JSON ──► FastAPI ──► validation ──► model ──► JSON response
```

> **The API does not train the model. It only loads a validated artifact and performs inference.**

## 2. Repository structure

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
├── client_examples.py
├── requests.http
├── STUDENT_GUIDE.md
├── EXERCISES.md
└── TROUBLESHOOTING.md
```

## 3. Create the Conda environment

```bash
conda env create -f environment.yml
conda activate awesome-api-resources
```

Existing environment:

```bash
conda env update -f environment.yml --prune
conda activate awesome-api-resources
```

Verify:

```bash
python --version
python -c "import fastapi, sklearn; print(fastapi.__version__, sklearn.__version__)"
```

## 4. Execute the training notebook

```bash
jupyter lab
```

Open `notebooks/01_train_iris_model.ipynb` and run top-to-bottom.

At each section ask:

1. What exists in memory now?
2. What is persisted to disk?
3. What will the API need later?
4. What breaks if the feature schema changes?

The committed notebook contains executed outputs for comparison with a known-good run.

## 5. Inspect the model package

```text
artifacts/
├── iris_model.joblib
├── model_metadata.json
└── metrics.json
```

- **model**: how to preprocess and predict;
- **metadata**: what the model expects and which version it is;
- **metrics**: how it performed before deployment.

## 6. HTTP contract

Request:

```json
{
  "sepal_length_cm": 5.1,
  "sepal_width_cm": 3.5,
  "petal_length_cm": 1.4,
  "petal_width_cm": 0.2
}
```

Response:

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

Flow:

```text
HTTP JSON
   ↓
Pydantic validation
   ↓
ordered DataFrame
   ↓
StandardScaler → LogisticRegression
   ↓
typed response
   ↓
HTTP JSON
```

## 7. Test before serving

```bash
pytest -q
# or
python test_api.py
```

The tests verify startup, liveness, readiness, model information, single prediction, batch prediction, probability consistency, invalid input, batch limits, request headers, and OpenAPI generation.

## 8. Start the local service

```bash
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

- `uvicorn`: ASGI application server;
- `app:app`: module `app.py`, FastAPI object `app`;
- `127.0.0.1`: local machine only;
- `8000`: TCP port;
- `--reload`: development-only auto-reload.

## 9. Explore the service

| URL | Purpose |
|---|---|
| `http://127.0.0.1:8000/` | service information |
| `http://127.0.0.1:8000/health/live` | liveness |
| `http://127.0.0.1:8000/health/ready` | readiness |
| `http://127.0.0.1:8000/model-info` | metadata + offline metrics |
| `http://127.0.0.1:8000/docs` | Swagger UI |
| `http://127.0.0.1:8000/redoc` | ReDoc |
| `http://127.0.0.1:8000/openapi.json` | OpenAPI specification |

## 10. Call it three ways

### Swagger
Open `/docs`, choose `POST /predict`, click **Try it out**.

### cURL

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

### Python

```bash
python client_examples.py
```

The client does not import the model; it talks to a separately running service over HTTP.

## 11. Liveness vs readiness

**Liveness:** is the application process alive?

`GET /health/live`

**Readiness:** has the model loaded, and can this instance serve useful traffic?

`GET /health/ready`

This distinction becomes important for containers, load balancers, and Kubernetes.

## 12. Why load the model once?

Bad:

```text
request → load model → predict
request → load model → predict
```

Correct:

```text
startup → load model once → ready
                         ├─ request → predict
                         ├─ request → predict
                         └─ request → predict
```

The FastAPI lifespan hook demonstrates this lifecycle.

## 13. Training-serving skew

The serialized scikit-learn Pipeline contains:

```text
raw features → StandardScaler → LogisticRegression
```

The API does not recreate preprocessing independently. This reduces training-serving skew.

## 14. Basic observability

Every response receives:

- `X-Request-ID`;
- `X-Process-Time-Ms`.

The server logs method, path, status, request ID, and processing time. Later modules will replace this introductory mechanism with production-grade observability patterns.

## 15. What is intentionally deferred?

Authentication, TLS, secrets, Docker, registry, cloud networking, autoscaling, centralized logs/metrics/traces, rate limiting, CI/CD, model registry, rollback, and progressive deployment are later stages—not missing concepts.

## 16. Cloud mapping

```text
TODAY
client → localhost:8000 → FastAPI → artifact

LATER
client → DNS/HTTPS → gateway/load balancer → container replicas → FastAPI → artifact
```

Infrastructure gets more sophisticated; the model-serving contract remains recognizable.

## Completion criteria

Before Docker, you should be able to:

- [ ] explain build time vs run time;
- [ ] recreate the Conda environment;
- [ ] execute the notebook successfully;
- [ ] explain every artifact;
- [ ] run tests;
- [ ] start Uvicorn;
- [ ] make valid and invalid requests;
- [ ] explain HTTP `422`;
- [ ] explain liveness vs readiness;
- [ ] explain OpenAPI/Swagger;
- [ ] explain why the model loads once;
- [ ] explain training-serving skew;
- [ ] map this service to a future container/cloud architecture.

Continue with [STUDENT_GUIDE.md](STUDENT_GUIDE.md), [EXERCISES.md](EXERCISES.md), and [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
