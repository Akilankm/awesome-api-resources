# Awesome API Resources — Professional Cloud & Deployment Track

A hands-on learning repository for students studying **APIs, model serving, cloud engineering, and deployment**.

This repository is designed as course material, not as a collection of isolated snippets. Every module should answer four questions:

1. **What problem are we solving?**
2. **Why is the architecture designed this way?**
3. **How do I run and verify it myself?**
4. **How does this map to real cloud and production systems?**

## Learning journey

```text
Python / ML model
      ↓
Model artifact
      ↓
FastAPI service
      ↓
Local testing
      ↓
Docker image
      ↓
Container registry
      ↓
Cloud runtime
      ↓
CI/CD
      ↓
Observability + scaling + security
```

## Course modules

| Stage | Module | Outcome |
|---|---|---|
| 01 | [Iris ML model serving with FastAPI](examples/01-iris-fastapi-local-serving/) | Understand offline training vs online inference, API contracts, local serving, validation, testing, Swagger/OpenAPI, and deployment readiness |
| 02 | Dockerizing the FastAPI service *(planned)* | Build an immutable container image and understand ports, processes, layers, and health checks |
| 03 | CI/CD *(planned)* | Automatically test, build, and validate every change |
| 04 | Container registry *(planned)* | Version and publish deployable images |
| 05 | Cloud deployment *(planned)* | Deploy the same container to a managed cloud runtime |
| 06 | Observability and reliability *(planned)* | Add logs, metrics, readiness, latency, scaling, and operational checks |

## Student resources

- [Course roadmap](docs/COURSE_ROADMAP.md)
- [API and deployment glossary](docs/GLOSSARY.md)
- [Deployment checklist](docs/DEPLOYMENT_CHECKLIST.md)

## Teaching philosophy

The repository deliberately keeps **model development**, **artifact packaging**, and **online serving** as separate lifecycle stages.

```text
BUILD TIME                                  RUN TIME
──────────                                  ────────
Data                                        HTTP request
  ↓                                             ↓
Training notebook                         FastAPI validation
  ↓                                             ↓
Evaluation                                Serialized artifact
  ↓                                             ↓
Model + metadata + metrics                Prediction
                                                ↓
                                           JSON response
```

That boundary remains valid whether the service runs on a laptop, Docker, Kubernetes, Azure, AWS, GCP, or another managed platform.

## How to use this repository

For each module:

1. Read the module README before running code.
2. Create the provided Conda environment.
3. Execute the notebook and inspect every output.
4. Rebuild the artifacts yourself.
5. Run the automated tests.
6. Start the API locally.
7. Explore Swagger/OpenAPI.
8. Complete the student exercises.
9. Review the production/cloud mapping before moving to the next stage.

> The goal is not merely to make an endpoint return `200 OK`. The goal is to understand the full engineering path from a trained model to a dependable deployable service.
