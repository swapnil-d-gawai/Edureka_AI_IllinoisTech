"""Model and benchmark a concurrent vendor health-monitoring workflow."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import wraps
import argparse
import asyncio
import json
import logging
from pathlib import Path
import random
import time
from typing import Any, Awaitable, Callable, ParamSpec, TypeVar


P = ParamSpec("P")
R = TypeVar("R")
LOGGER = logging.getLogger("vendor-monitor")


class VendorError(RuntimeError):
    """A vendor could not provide a usable health result."""


def timed(function: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
    """Measure an async function while preserving its metadata and result contract."""
    @wraps(function)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        """Await the wrapped operation and log elapsed time even when it raises."""
        started = time.perf_counter()
        try:
            return await function(*args, **kwargs)
        finally:
            LOGGER.debug("%s took %.3fs", function.__name__, time.perf_counter() - started)

    return wrapper


class VendorClient(ABC):
    """Contract for interchangeable vendor-health implementations."""

    @abstractmethod
    async def check(self, vendor: str) -> dict[str, Any]:
        """Return a vendor health mapping or raise VendorError."""


@dataclass(frozen=True)
class MockVendorClient(VendorClient):
    """Deterministic local client used to teach latency, results, and failures."""

    seed: int = 17
    failure_vendors: frozenset[str] = frozenset()

    async def check(self, vendor: str) -> dict[str, Any]:
        """Return a seeded result after a simulated network wait."""
        # Seeded randomness makes a named vendor reproducible across runs.
        delay = random.Random(f"{self.seed}:{vendor}").uniform(0.05, 0.2)
        await asyncio.sleep(delay)
        if vendor in self.failure_vendors:
            raise VendorError(f"{vendor} timed out")
        status_seed = random.Random(f"status:{self.seed}:{vendor}").random()
        return {
            "vendor": vendor,
            "healthy": status_seed > 0.2,
            "latency_ms": round(delay * 1000),
            "provider": "mock",
        }


async def safe_check(client: VendorClient, vendor: str) -> dict[str, Any]:
    """Translate expected client failures into reportable per-vendor results."""
    try:
        return await client.check(vendor)
    except VendorError as exc:
        LOGGER.warning("vendor check failed: %s", exc)
        return {"vendor": vendor, "healthy": False, "error": str(exc)}
    except Exception:
        LOGGER.exception("unexpected vendor error for %s", vendor)
        return {"vendor": vendor, "healthy": False, "error": "internal error"}


@timed
async def concurrent_checks(client: VendorClient, vendors: list[str], limit: int) -> list[dict[str, Any]]:
    """Overlap independent waits while bounding active client operations."""
    semaphore = asyncio.Semaphore(limit)

    async def bounded(vendor: str) -> dict[str, Any]:
        """Acquire one concurrency slot before making a vendor call."""
        async with semaphore:
            return await safe_check(client, vendor)

    return await asyncio.gather(*(bounded(vendor) for vendor in vendors))


@timed
async def sequential_checks(client: VendorClient, vendors: list[str]) -> list[dict[str, Any]]:
    """Provide a directly comparable baseline that checks one vendor at a time."""
    return [await safe_check(client, vendor) for vendor in vendors]


async def run(vendors: list[str], output: Path, limit: int) -> dict[str, Any]:
    """Benchmark both execution strategies and write a parity-checked report."""
    if not vendors or any(not name.strip() for name in vendors):
        raise ValueError("at least one non-empty vendor is required")
    if len(set(vendors)) != len(vendors):
        raise ValueError("vendor names must be unique")
    if limit < 1:
        raise ValueError("concurrency limit must be positive")
    client = MockVendorClient(failure_vendors=frozenset({"payments-gateway"}))
    started = time.perf_counter()
    sequential = await sequential_checks(client, vendors)
    sequential_elapsed = time.perf_counter() - started
    started = time.perf_counter()
    concurrent = await concurrent_checks(client, vendors, limit)
    concurrent_elapsed = time.perf_counter() - started
    report = {
        "results": concurrent,
        "sequential_elapsed_seconds": round(sequential_elapsed, 4),
        "concurrent_elapsed_seconds": round(concurrent_elapsed, 4),
        "speedup": round(sequential_elapsed / max(concurrent_elapsed, 0.0001), 2),
        "healthy_count": sum(bool(row["healthy"]) for row in concurrent),
        "result_parity": sorted(row["vendor"] for row in sequential)
        == sorted(row["vendor"] for row in concurrent),
    }
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    """Parse command options and translate expected failures into process status."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--vendors",
        nargs="+",
        default=["identity", "search-index", "payments-gateway", "email", "documents"],
    )
    parser.add_argument("--concurrency", type=int, default=3)
    parser.add_argument("--output", type=Path, default=Path("vendor_health_report.json"))
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s %(message)s")
    try:
        report = asyncio.run(run(args.vendors, args.output, args.concurrency))
        print(json.dumps({key: report[key] for key in ("healthy_count", "speedup", "result_parity")}, indent=2))
        return 0
    except (OSError, ValueError) as exc:
        LOGGER.error("cannot run monitor: %s", exc)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
