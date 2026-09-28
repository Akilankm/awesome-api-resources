# Student Exercises

## Level 1 — API fundamentals

### Exercise 1: Break the request schema

Try:
1. omit `petal_width_cm`;
2. send `"five"`;
3. send a negative measurement;
4. send an extra field.

Record the HTTP response and explain which layer rejected it.

### Exercise 2: Method vs path

Try:

```text
GET /predict
POST /health/live
GET /does-not-exist
```

Explain `404` vs `405`.

## Level 2 — Model-serving contract

### Exercise 3: Add confidence

Add `confidence` equal to the highest class probability.

Requirements:
- update the response model;
- update prediction logic;
- update tests;
- verify OpenAPI changes.

### Exercise 4: Build metadata

Expose and explain `created_at_utc` through `/model-info`.

## Level 3 — Reliability

### Exercise 5: Missing model

Temporarily rename `artifacts/iris_model.joblib` and start the app.

Explain:
- what fails;
- when it fails;
- whether traffic should be accepted;
- how readiness should behave.

### Exercise 6: Batch limit

Send 101 items to `/predict/batch`. Explain why bounded batch size protects services.

## Level 4 — Architecture

### Exercise 7: Draw production

Extend:

```text
client → ? → ? → FastAPI → model
```

Include HTTPS, DNS, load balancer/API gateway, two replicas, centralized logging, and metrics/alerts.

### Exercise 8: Why not retrain on startup?

Explain why this is undesirable:

```python
@app.on_event("startup")
def startup():
    model = train_model_from_raw_data()
```

Discuss startup time, reproducibility, availability, versioning, and rollback.

## Capstone extension

Replace Iris with another scikit-learn tabular classification dataset while preserving:

```text
notebook → artifacts → API contract → tests → local serving
```
