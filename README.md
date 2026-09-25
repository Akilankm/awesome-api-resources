# awesome-api-resources

A practical learning repository for **APIs, model serving, cloud, and deployment** with executable examples.

The resources are organized as progressive deployment stages rather than isolated code snippets.

## Learning path

| Stage | Resource | What it teaches |
|---|---|---|
| 01 | [Iris ML Model Serving with FastAPI](examples/01-iris-fastapi-local-serving/) | Train a model offline, create artifacts, load them into FastAPI, validate HTTP requests, and serve inference locally |

## Core deployment principle

```text
Develop → Train → Evaluate → Package artifacts → Serve → Test → Containerize → Deploy → Observe
```

The first example intentionally stops at **tested local serving**. This makes the boundary between ML training and online inference explicit before containers and cloud infrastructure are introduced.
