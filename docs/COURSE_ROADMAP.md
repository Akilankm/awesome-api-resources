# Professional Course Roadmap

## Target learner

This track is intended for students who already know basic Python and have seen at least one machine-learning workflow, but are new to **API engineering, deployment, containers, cloud runtimes, and production ML serving**.

## Learning outcomes

By the end of the track, a student should be able to explain and implement:

- training vs model serving;
- model serialization and artifact packaging;
- HTTP requests, responses, status codes, JSON, and API contracts;
- FastAPI validation and response schemas;
- local model serving with Uvicorn;
- automated API testing;
- liveness vs readiness;
- OpenAPI and Swagger;
- Docker and container runtime concepts;
- registries and image versioning;
- cloud deployment patterns;
- configuration, secrets, logging, monitoring, scaling, and CI/CD;
- common production failures such as schema drift and training-serving skew.

## Progressive architecture

### Stage 01 — Local model serving
```text
Notebook → model artifact → FastAPI → Uvicorn → localhost
```

### Stage 02 — Containerization
```text
FastAPI + artifact + dependencies → Docker image → local container
```

### Stage 03 — CI/CD
```text
Git push → tests → build → quality checks → image
```

### Stage 04 — Registry
```text
versioned image → registry → immutable deployment input
```

### Stage 05 — Cloud runtime
```text
registry → managed runtime / VM / Kubernetes → endpoint
```

### Stage 06 — Production operations
```text
traffic → load balancer → replicas → logs + metrics + alerts → autoscaling
```

## Recommended learning loop

```text
Concept → Architecture → Build → Run → Inspect → Break → Debug → Test → Extend
```

Students should be able to predict what will happen before running a command. That is the point where deployment stops being memorized syntax and becomes an engineering mental model.
