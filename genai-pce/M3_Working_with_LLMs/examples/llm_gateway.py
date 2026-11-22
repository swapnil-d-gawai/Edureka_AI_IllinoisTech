"""Offline provider boundary, parameter validation, retries, and usage metrics.

All failures are simulated locally so transport and validation behavior can be
studied without an SDK, key, or network call.
"""

from dataclasses import dataclass
from time import monotonic, sleep
from typing import Protocol


class TransientProviderError(Exception):
    pass


@dataclass(frozen=True)
class GenerationSettings:
    # Frozen settings represent a per-request configuration that validators can
    # audit without later accidental mutation.
    temperature: float = 0.2
    top_p: float = 0.9
    max_tokens: int = 180
    timeout_seconds: float = 5.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("temperature must be between 0 and 2")
        if not 0.0 < self.top_p <= 1.0:
            raise ValueError("top_p must be greater than 0 and at most 1")
        if not 1 <= self.max_tokens <= 4_096:
            raise ValueError("max_tokens must be between 1 and 4096")
        if not 0.0 < self.timeout_seconds <= 60.0:
            raise ValueError("timeout_seconds must be between 0 and 60")


@dataclass(frozen=True)
class Request:
    request_id: str
    system: str
    user: str
    settings: GenerationSettings

    def __post_init__(self) -> None:
        if not self.request_id.strip() or not self.system.strip() or not self.user.strip():
            raise ValueError("request_id, system, and user must be non-empty")
        estimated = estimate_tokens(self.system + self.user)
        if estimated > 16_000:
            raise ValueError("input exceeds this exercise's 16000-token safety limit")


@dataclass(frozen=True)
class Response:
    # Operations data is returned separately from prose so cost/latency can be tested.
    text: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    attempts: int
    estimated_cost_usd: float


class Provider(Protocol):
    # Adapters must enforce this per-call timeout; the gateway cannot interrupt a
    # synchronous provider that ignores it.
    def complete(self, request: Request, *, timeout_seconds: float) -> str: ...


class MockProvider:
    # A stateful mock deliberately models a finite sequence of transient failures.
    def __init__(self, transient_failures: int = 0, malformed: bool = False) -> None:
        self._remaining_failures = transient_failures
        self._malformed = malformed

    def complete(self, request: Request, *, timeout_seconds: float) -> str:
        if not 0.0 < timeout_seconds <= request.settings.timeout_seconds:
            raise ValueError("provider timeout must be bounded by the request budget")
        if self._remaining_failures:
            self._remaining_failures -= 1
            raise TransientProviderError("simulated 429 throttle")
        if self._malformed:
            return '{"category": "incident",}'
        return "Incident triage complete: verify policy evidence before taking action."


def estimate_tokens(text: str) -> int:
    # Four characters per token is only a readable teaching estimate, not a tokenizer.
    return max(1, (len(text) + 3) // 4)


def run(
    request: Request,
    provider: Provider,
    *,
    max_attempts: int = 3,
    base_delay_seconds: float = 0.01,
) -> Response:
    if not 1 <= max_attempts <= 5 or base_delay_seconds < 0:
        raise ValueError("invalid retry configuration")
    # End-to-end timing includes retry delays, matching the caller's real wait.
    started = monotonic()
    deadline = started + request.settings.timeout_seconds
    for attempt in range(1, max_attempts + 1):
        remaining = deadline - monotonic()
        if remaining <= 0.0:
            raise TimeoutError("generation deadline reached before provider call")
        try:
            text = provider.complete(request, timeout_seconds=remaining)
            if not text.strip():
                raise RuntimeError("provider returned an empty completion")
            output = text[: request.settings.max_tokens * 4]
            elapsed = monotonic() - started
            if elapsed >= request.settings.timeout_seconds:
                raise TimeoutError("generation exceeded configured deadline")
            input_tokens = estimate_tokens(request.system + request.user)
            output_tokens = estimate_tokens(output)
            # Illustrative rates only; real pricing must be versioned from a provider.
            estimated_cost = input_tokens * 0.000001 + output_tokens * 0.000003
            return Response(
                output,
                input_tokens,
                output_tokens,
                elapsed * 1_000,
                attempt,
                estimated_cost,
            )
        except TransientProviderError:
            if attempt == max_attempts:
                raise
            # Exponential backoff bounds repeated load; production code should add jitter.
            delay = base_delay_seconds * (2 ** (attempt - 1))
            remaining = deadline - monotonic()
            if remaining <= 0.0 or delay >= remaining:
                raise TimeoutError("retry backoff would exceed generation deadline") from None
            sleep(delay)
    raise AssertionError("unreachable")


def validate_mock_json(text: str) -> dict[str, str]:
    # Parsing and schema checks occur after the provider boundary; model output is data,
    # not trusted application state.
    import json

    value = json.loads(text)
    if not isinstance(value, dict) or not isinstance(value.get("category"), str):
        raise ValueError("response did not match category contract")
    return value


def main() -> None:
    request = Request(
        "req-17",
        "Return a concise, evidence-based support assessment.",
        "The customer reports a delayed shipment and requests escalation.",
        GenerationSettings(),
    )
    # Attempt 3 succeeds, demonstrating a bounded retry path.
    response = run(request, MockProvider(transient_failures=2))
    print(response)

    capped_request = Request(
        "req-cap",
        "Return a short answer.",
        "Demonstrate the output cap.",
        GenerationSettings(max_tokens=1),
    )

    class RecordingProvider(MockProvider):
        def __init__(self) -> None:
            super().__init__()
            self.last_timeout = 0.0

        def complete(self, request: Request, *, timeout_seconds: float) -> str:
            self.last_timeout = timeout_seconds
            return super().complete(request, timeout_seconds=timeout_seconds)

    recording_provider = RecordingProvider()
    capped = run(capped_request, recording_provider)
    assert len(capped.text) == 4 and capped.output_tokens == 1
    assert 0.0 < recording_provider.last_timeout <= capped_request.settings.timeout_seconds

    deadline_request = Request(
        "req-deadline",
        "Return an answer.",
        "Demonstrate retry deadline enforcement.",
        GenerationSettings(timeout_seconds=0.001),
    )
    try:
        run(
            deadline_request,
            MockProvider(transient_failures=1),
            max_attempts=2,
            base_delay_seconds=1.0,
        )
    except TimeoutError:
        pass
    else:
        raise AssertionError("retry backoff should not be scheduled beyond the deadline")

    try:
        # This trailing comma intentionally makes JSON invalid and exercises safe
        # escalation rather than silently repairing a malformed response.
        malformed = run(request, MockProvider(malformed=True))
        validate_mock_json(malformed.text)
    except (ValueError, TypeError) as error:
        print(f"Malformed output escalated safely: {error}")


if __name__ == "__main__":
    main()
