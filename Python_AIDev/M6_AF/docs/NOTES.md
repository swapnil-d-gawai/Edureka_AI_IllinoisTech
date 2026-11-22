# Module 6 Notes: AI APIs and FastAPI Backends

These notes follow the LMS map for REST/HTTP, FastAPI structure, request/response models, async AI endpoints, Server-Sent Events, uploads, Uvicorn, Swagger, and testing. An API is a production contract, not simply a Python function exposed on a port.

## 1. Request-response mental model

A client sends:

1. an HTTP method,
2. a path,
3. headers,
4. optionally a body.

The server responds with status, headers, and optionally a body. A scheduler making a REST call is analogous to a remote job invocation, except state and status are communicated through the HTTP protocol.

Example:

```http
POST /tickets
Content-Type: application/json

{"subject":"Checkout unavailable","body":"All users receive an error","service":"checkout"}
```

An expected response starts with `201 Created` and a structured ticket result.

## 2. REST resource design

REST commonly represents resources with nouns:

- `GET /tickets`: retrieve collection,
- `POST /tickets`: create a ticket,
- `GET /tickets/{id}`: retrieve one,
- `PATCH /tickets/{id}`: partial update,
- `PUT /tickets/{id}`: full replacement,
- `DELETE /tickets/{id}`: remove where allowed.

For an action that is not naturally a resource, be explicit and idempotent where possible. Do not invent a method based only on what implementation code calls internally.

## 3. HTTP status codes

| Class | Meaning |
| --- | --- |
| 2xx | request succeeded |
| 3xx | redirect/alternate representation |
| 4xx | request/client/account issue |
| 5xx | server/dependency failure |

Useful contracts:

- `200`: retrieved/processed successfully,
- `201`: created,
- `204`: successful, intentionally no body,
- `400`: malformed request not captured by schema,
- `401`: authentication required/failed,
- `403`: authenticated but not permitted,
- `404`: resource absent according to policy,
- `409`: state conflict,
- `422`: FastAPI/Pydantic schema validation,
- `429`: rate limited,
- `503`: dependency temporarily unavailable.

Do not return `200` with `{"error":...}` for ordinary machine clients; the status code is part of the contract.

## 4. FastAPI from the smallest building blocks

```python
app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

- `app` is the ASGI application.
- `@app.get` registers a route decorator.
- `health` is the handler.
- a dictionary becomes a JSON-compatible response.
- `async def` is useful when the route awaits non-blocking I/O.

FastAPI reads Python type annotations to create validation and OpenAPI documentation. Annotation accuracy matters because it becomes runtime/API behavior.

## 5. Pydantic models

```python
class TicketCreate(BaseModel):
    subject: str = Field(min_length=3, max_length=160)
```

Pydantic validates incoming values and can serialize output models. It is a schema boundary—like a strongly defined Informatica target structure—but it still depends on accurate business rules.

Request model concerns:

- required fields,
- types/ranges/lengths,
- nested structures,
- normalization policy,
- unknown-field behavior.

Response model concerns:

- stable public fields,
- sensitive fields excluded,
- predictable formats,
- validation before sending.

A response model should not expose an entire internal dictionary merely because that is convenient.

## 6. Enums, annotations, and `Annotated`

An `Enum` constrains allowed values:

```python
class Severity(str, Enum):
    low = "low"
    high = "high"
```

FastAPI can reject `"urgent"` before classification.

`Annotated[T, ...]` attaches metadata to a type:

```python
severity: Annotated[Severity | None, Query()] = None
```

The type describes the value; `Query()` tells FastAPI where to obtain it and may carry constraints. Beginners can read this in two pieces rather than treating all syntax as one mystery.

## 7. Dependency injection

Dependency injection supplies collaborators rather than hard-coding them in the route:

```python
def classifier_dependency() -> Classifier:
    return OptionalExternalClassifier()

async def create_ticket(classifier: Annotated[Classifier, Depends(classifier_dependency)]):
    ...
```

Why this matters:

- tests can replace model/provider clients,
- production can change configuration,
- routes stay focused on protocol and orchestration,
- local practice needs no paid/network service.

This is similar to swapping an Informatica connection rather than changing every transformation.

## 8. Async provider calls

Use `await` only for awaitable non-blocking operations. A synchronous model/file/network call inside `async def` can block the server event loop and delay unrelated requests.

For a real external AI provider:

- set a finite timeout,
- bound retries and rate limiting,
- define retriable statuses,
- redact/log correlation IDs,
- avoid logging prompt/response data by default,
- validate provider output,
- keep the provider behind an interface.

The example uses deterministic local rules. `TRIAGE_PROVIDER_ENDPOINT` deliberately returns a `503` placeholder rather than pretending to make an undocumented network call.

## 9. Server-Sent Events

SSE is a one-way server-to-client stream over HTTP:

```text
data: Checkout

data: unavailable

event: complete
data: done

```

Each event ends in a blank line. The media type is `text/event-stream`.

Use SSE for progressive output such as generated text. It complements JSON endpoints; do not use a stream to hide errors or create an indefinitely open request with no timeout/disconnect handling.

Bound token/event counts, check client disconnection, and authenticate according to the surrounding API policy.

## 10. Uploads

Before reading or model-processing a file:

- authenticate/authorize,
- enforce count/byte limits,
- verify media type/content,
- sanitize an untrusted filename,
- stream large content rather than loading all into memory,
- scan if policy requires,
- process heavy extraction outside the request thread/process.

A declared `.pdf` extension or content type is not proof that bytes are a PDF. Store only after validation.

## 11. In-memory store and real persistence

```python
class TicketStore:
    def __init__(self):
        self._items = {}
```

This demonstrates the repository-like boundary. It resets on process restart and is not safe for concurrent durability or multiple workers. Production adds a database, transactional behavior, retention, and migration/versioning.

List endpoints should return copies/public DTOs rather than leaking mutable internal objects.

## 12. Exception mapping

The route catches `RuntimeError` from the configured provider:

```python
except RuntimeError as exc:
    raise HTTPException(status_code=503, detail=str(exc)) from exc
```

`from exc` preserves the cause for server-side diagnosis. Only expose safe details to clients. Do not expose a stack trace or raw provider secret.

## 13. Running and generated documentation

Uvicorn is an ASGI server:

```bash
cd examples
uvicorn support_triage_api:app --reload
```

`--reload` watches files and is for development, not production multi-worker operation. OpenAPI is served as schema, and Swagger UI is usually at `/docs`.

The documentation comes from routes, annotations, and models. It should agree with tests; generated docs alone do not prove behavior.

## 14. Worked route flow

Input:

```json
{
  "subject": "Checkout unavailable",
  "body": "All users receive an error during payment",
  "service": "checkout"
}
```

Flow:

1. Pydantic checks lengths and strings.
2. dependency creates the classifier,
3. route awaits classification,
4. result `TriageResult` is constructed,
5. store saves the result,
6. FastAPI serializes and returns `201`.

The local rules recognize `"unavailable"` and `"all users"` as high severity and route to `service-desk-l2`.

Invalid body lengths produce `422`. A ticket ID not saved by this process produces `404`.

## 15. Testing checklist

Test:

- happy path and exact response fields,
- status codes, not only body,
- invalid/missing/too-long payloads,
- unknown and malformed IDs,
- authentication/authorization if introduced,
- dependency replacement,
- provider timeout/unavailable behavior,
- SSE framing/disconnect,
- store side effects,
- concurrency/idempotency where relevant.

Use a local deterministic client; do not let CI depend on a paid external model.

## 16. Debugging checklist

1. Read the status and response body together.
2. For `422`, inspect each Pydantic `loc` and message.
3. Confirm method/path, JSON `Content-Type`, and server URL.
4. Inspect the route registration in `/openapi.json`.
5. Replace provider dependency with a mock.
6. Check sync/blocking calls inside async handlers.
7. Confirm server process/module import context.
8. Use correlation IDs in logs without recording sensitive payloads.

## 17. Common mistakes

- A response model mismatching the handler's return value.
- Using `str(e)` as public error detail.
- Treating `async def` as automatic concurrency.
- Reading unbounded request/file content.
- Returning mutable internal state.
- Wrong status code semantics.
- Secrets sent into docs, logs, validation errors, or provider calls.

## 18. Practice

1. Define a `PATCH /tickets/{id}` request with one optional field.
2. Write tests for `201`, `422`, `404`, and `503`.
3. Inject a fake classifier recording call count and arguments.
4. Add timeout to a mock provider and return a safe `503`.
5. Add upload limits and test one oversized file.
6. Consume the SSE endpoint with a client and verify blank-line termination.
7. Replace `TicketStore` with a file-backed store; describe its concurrency limitations.

## 19. LMS demonstration walkthrough

**Exact resource:** [demonstration 8622](https://lms.snvaveranda.com/mod/resource/view.php?id=8622).

### Actual scenario and data

The LMS walk-through creates an AI backend: a FastAPI application accepts a prompt, validates it with Pydantic, sends it to Groq, and returns generated text with the model name and success status. It also adds environment-based configuration, a health/root check, Uvicorn, Swagger UI, and a Python HTTP client.

Use the public contract in abstract:

```json
{"prompt":"Explain a batch retry policy in two sentences."}
```

```json
{"response":"<provider text>","model":"<configured model>","status":"success"}
```

These are synthetic shapes, not copied responses. The provider key is configuration, not request data, and must be read from the local environment or an ignored `.env`.

### Step-by-step beginner workflow

1. Create a `PromptRequest` with a constrained non-empty string and a `PromptResponse` with `response`, `model`, and `status`.
2. Add `GET /` and verify `{"message": ...}` before involving a provider.
3. Add a local deterministic generator behind a small function/dependency; this makes validation and route behavior testable offline.
4. Run Uvicorn and inspect both `/docs` and `/openapi.json`.
5. Submit one valid request and then missing, wrong-type, and extra-field variants. Record status and validation locations.
6. Add a provider adapter with a finite timeout and environment key. Translate provider failures to a safe service error.
7. Confirm response serialization matches the response model.
8. Call the endpoint through a client and assert method, URL, status, content type, and required response fields.
9. Review Git status to prove no `.env` or key can be committed.

### Connection to the current examples

`support_triage_api.py` is an **original extension beyond the LMS Groq endpoint**. It uses FastAPI/Pydantic and an injectable model-like collaborator, but its ticket schema, status semantics, repository, filtering, and SSE stream are independently designed. It remains local/offline by default and intentionally returns `503` for an undeclared external provider rather than pretending to call one.

### Deliberate practice

Write a table with valid, absent prompt, blank prompt, provider timeout, and provider invalid-response cases. Predict the exact HTTP status and safe public body. Replace the dependency with a fake that records its arguments; verify no secret reaches it through logs or response output. Run the same invalid request in Swagger and through a client and compare their evidence.
