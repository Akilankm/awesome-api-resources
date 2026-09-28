# Troubleshooting Guide

## `conda: command not found`
Install Miniconda/Anaconda or initialize Conda, then verify with `conda --version`.

## Environment already exists
```bash
conda env update -f environment.yml --prune
conda activate awesome-api-resources
```

## `ModuleNotFoundError`
```bash
python -c "import sys; print(sys.executable)"
conda info --envs
```
A common cause is launching Jupyter/Uvicorn from another environment.

## Model loading fails
Verify:
```text
artifacts/iris_model.joblib
artifacts/model_metadata.json
artifacts/metrics.json
```
If missing, execute the notebook completely.

## Address already in use
```bash
uvicorn app:app --port 8001
```

## HTTP 422
The request reached FastAPI but failed Pydantic validation. Compare with `/docs`.

## HTTP 404
Check the route path.

## HTTP 405
The route exists but the HTTP method is wrong.

## Notebook writes artifacts to the wrong place
Start Jupyter from the module directory or use the committed notebook path logic.

## Notebook prediction and API prediction differ
Check feature names, order, units, preprocessing, and artifact version. This is the training-serving-skew debugging path.

## Tests fail because Uvicorn is not running
The tests use `TestClient` and start the FastAPI app in-process. A separate Uvicorn process is not required.
