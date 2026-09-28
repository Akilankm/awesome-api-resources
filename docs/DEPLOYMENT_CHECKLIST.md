# Deployment Readiness Checklist

Use this checklist as the course progresses.

## Model and artifacts

- [ ] Training is separate from API startup.
- [ ] Preprocessing is packaged with the estimator where practical.
- [ ] Feature names/order are explicit.
- [ ] Model version is recorded.
- [ ] Evaluation metrics are stored.
- [ ] Serialized artifact is reloaded and tested before serving.

## API contract

- [ ] Request schema is explicit.
- [ ] Response schema is explicit.
- [ ] Invalid requests return appropriate `4xx` responses.
- [ ] API exposes liveness/readiness.
- [ ] OpenAPI/Swagger is available.
- [ ] Batch behavior and limits are defined.

## Runtime

- [ ] Dependencies are reproducible.
- [ ] Startup fails clearly when required artifacts are missing.
- [ ] Model is loaded once rather than once per request.
- [ ] Logs provide useful startup/request context.
- [ ] Automated tests verify core behavior.

## Container/cloud stages

- [ ] Application is containerized.
- [ ] Image version is traceable to source.
- [ ] Configuration is separated from code.
- [ ] Secrets are not stored in the repository.
- [ ] Liveness/readiness probes are configured.
- [ ] Resource limits are defined where applicable.
- [ ] Logs and metrics are collected.
- [ ] Alerts exist for important failures.
- [ ] Deployment supports rollback.
- [ ] CI/CD runs tests before release.
