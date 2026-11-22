# Support triage API

`support_triage_api.py` provides validated ticket creation, retrieval, severity filtering, deterministic classification, and an SSE summary stream. The route depends on a replaceable classifier and uses explicit 201, 404, 422, 503, and 200 contracts.

Requires `fastapi` and an ASGI server such as `uvicorn`, already used by the course environment:

```bash
cd examples
uvicorn support_triage_api:app --reload
```

Visit `http://127.0.0.1:8000/docs`. Try:

```json
{"subject":"Checkout unavailable","body":"All users receive an error during payment","service":"checkout"}
```

The default classifier is local and requires no network. `TRIAGE_PROVIDER_ENDPOINT` demonstrates an isolated integration boundary and returns 503 instead of making an undeclared external call.

Challenges: add dependency injection tests with `TestClient`, an update endpoint, rate limiting, upload validation, bounded SSE events, and a real provider adapter using a documented timeout and mock server.
