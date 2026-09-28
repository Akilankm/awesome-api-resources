# Student Guide — From Python Model to Network Service

## The key conceptual transition

A model inside a notebook is a Python object available only to that Python process.

```python
prediction = model.predict(X)
```

Serving introduces a network boundary:

```text
APPLICATION A                              MODEL SERVICE
create request JSON
       │
       ├──────────── HTTP ────────────────► FastAPI
                                             │
                                             ▼
                                         model.predict()
                                             │
       ◄──────────── JSON ───────────────────┤
       │
consume prediction
```

## Follow one request end to end

1. Uvicorn receives HTTP on port 8000.
2. FastAPI matches method + route, e.g. `POST /predict`.
3. JSON is decoded.
4. Pydantic validates fields, types, and constraints.
5. The API reconstructs features in metadata-defined order.
6. The serialized Pipeline runs preprocessing and inference.
7. Output is validated by the response model.
8. FastAPI serializes JSON back to the client.

## HTTP status codes to know

| Code | Meaning | Example |
|---:|---|---|
| 200 | success | valid prediction |
| 404 | route not found | `/predictt` |
| 405 | wrong HTTP method | `GET /predict` |
| 422 | schema/value validation failed | missing or invalid feature |
| 500 | unexpected server failure | unhandled application exception |
| 503 | service not ready | model unavailable |

## Development vs production

```bash
uvicorn app:app --reload
```

`--reload` is useful during development. Production systems normally use controlled process/container restarts and immutable releases.

## Debugging sequence

```text
1. Is the Conda environment active?
2. Do artifacts exist?
3. Can Python import app.py?
4. Does startup load the model?
5. Does /health/ready return 200?
6. Does /docs load?
7. Does a known-good request work?
8. Does the client send exactly the schema expected?
```

This boundary-by-boundary debugging method becomes even more important in cloud systems.
