# API & Deployment Glossary

| Term | Meaning in this course |
|---|---|
| API | A defined interface through which software systems communicate |
| Endpoint | A specific API route, such as `POST /predict` |
| HTTP | Application protocol used by the client and FastAPI service |
| Request | Data and metadata sent by a client to the server |
| Response | Data and HTTP status returned by the server |
| JSON | Text format used for request and response bodies |
| Schema | Expected structure and types of a request or response |
| Validation | Rejecting input that violates the schema or constraints |
| OpenAPI | Machine-readable specification describing an HTTP API |
| Swagger UI | Interactive browser UI generated from OpenAPI |
| Model artifact | Serialized trained model used for inference |
| Serialization | Converting an in-memory object into a storable/loadable representation |
| Inference | Using a trained model to generate predictions |
| Training-serving skew | Difference between training-time and serving-time feature/preprocessing semantics |
| Uvicorn | ASGI server process that runs the FastAPI application |
| ASGI | Python async server interface used by frameworks such as FastAPI |
| Liveness | Whether the application process is alive |
| Readiness | Whether the application can receive useful traffic |
| Latency | Time required to process a request |
| Throughput | Requests processed per unit time |
| Container | Isolated runtime packaging code and dependencies |
| Image | Immutable template used to start containers |
| Registry | Service storing and versioning container images |
| Deployment | Making a version of an application run in a target environment |
| Replica | One running application instance |
| Load balancer | Distributes traffic across instances |
| Observability | Understanding behavior through logs, metrics, and traces |
| CI/CD | Automated integration, testing, packaging, and deployment |
| Rollback | Returning to a previously known-good release |
