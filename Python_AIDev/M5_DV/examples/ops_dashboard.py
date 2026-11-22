"""Generate a multi-panel operational reliability dashboard."""

from __future__ import annotations

from pathlib import Path
import argparse
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def build_sample() -> pd.DataFrame:
    """Generate deterministic operational observations suitable for repeatable charts."""
    rng = np.random.default_rng(42)
    rows: list[dict[str, object]] = []
    services = ("checkout", "identity", "search", "recommendations")
    regions = ("north", "south")
    for day in pd.date_range("2026-01-01", periods=42, freq="D"):
        for service_index, service in enumerate(services):
            volume = int(rng.integers(700, 4000))
            latency = 140 + service_index * 35 + np.clip(rng.normal(20, 45), -40, 140)
            error_rate = np.clip(0.004 + service_index * 0.003 + rng.normal(0, 0.004), 0, 0.05)
            rows.append(
                {
                    "date": day,
                    "service": service,
                    "region": regions[(int(day.day) + service_index) % 2],
                    "requests": volume,
                    "latency_ms": round(float(latency), 1),
                    "error_rate": round(float(error_rate), 4),
                    "availability": round(1 - float(error_rate) * rng.uniform(0.4, 0.9), 5),
                }
            )
    return pd.DataFrame(rows)


def load_data(path: Path | None) -> pd.DataFrame:
    """Load and validate external observations, or use the repeatable sample."""
    if path is None:
        return build_sample()
    frame = pd.read_csv(path, parse_dates=["date"])
    required = {"date", "service", "region", "requests", "latency_ms", "error_rate", "availability"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")
    if frame.empty:
        raise ValueError("dataset must not be empty")
    if frame[list(required)].isna().any().any():
        raise ValueError("dataset contains missing required values")
    if (frame["requests"] < 0).any() or (frame["latency_ms"] < 0).any():
        raise ValueError("requests and latency must be non-negative")
    if not frame["error_rate"].between(0, 1).all():
        raise ValueError("error_rate must be between 0 and 1")
    if not frame["availability"].between(0, 1).all():
        raise ValueError("availability must be between 0 and 1")
    return frame


def make_dashboard(frame: pd.DataFrame, output: Path, latency_sla: float) -> dict[str, object]:
    """Aggregate one question per panel, export the figure, and report numeric evidence."""
    sns.set_theme(style="whitegrid", context="notebook")
    # Four named axes keep every chart target explicit instead of relying on global plot state.
    figure, axes = plt.subplots(2, 2, figsize=(14, 9))
    daily = frame.groupby("date", as_index=False).agg(
        requests=("requests", "sum"), error_rate=("error_rate", "mean"), latency_ms=("latency_ms", "mean")
    )
    sns.lineplot(data=daily, x="date", y="latency_ms", ax=axes[0, 0], color="#2463a6")
    axes[0, 0].axhline(latency_sla, color="#c0392b", linestyle="--", label=f"SLA {latency_sla:g} ms")
    axes[0, 0].set(title="Average latency trend", ylabel="Latency (ms)", xlabel="")
    axes[0, 0].tick_params(axis="x", rotation=30)
    axes[0, 0].legend()

    service = (
        frame.groupby("service", as_index=False)
        .agg(error_rate=("error_rate", "mean"), requests=("requests", "sum"))
        .sort_values("error_rate")
    )
    sns.barplot(data=service, x="error_rate", y="service", hue="service", legend=False, ax=axes[0, 1])
    axes[0, 1].set(title="Mean error rate by service", xlabel="Error rate", ylabel="")
    for container in axes[0, 1].containers:
        labels = [f"{bar.get_width() * 100:.2f}%" for bar in container]
        axes[0, 1].bar_label(container, labels=labels)

    sns.histplot(data=frame, x="latency_ms", hue="region", bins=18, element="step", ax=axes[1, 0])
    axes[1, 0].axvline(latency_sla, color="#c0392b", linestyle="--")
    axes[1, 0].set(title="Latency distribution", xlabel="Latency (ms)", ylabel="Observations")

    scatter_data = frame.groupby(["service", "region"], as_index=False).agg(
        requests=("requests", "mean"), availability=("availability", "mean")
    )
    sns.scatterplot(
        data=scatter_data,
        x="requests",
        y="availability",
        hue="service",
        style="region",
        size="requests",
        sizes=(40, 180),
        ax=axes[1, 1],
    )
    axes[1, 1].set(title="Volume versus availability", xlabel="Mean daily requests", ylabel="Availability")
    axes[1, 1].ticklabel_format(axis="y", style="plain")

    figure.suptitle("Service reliability review", fontsize=18, fontweight="bold")
    figure.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(figure)
    worst = service.iloc[-1]
    return {
        "rows": int(len(frame)),
        "date_start": str(frame["date"].min().date()),
        "date_end": str(frame["date"].max().date()),
        "highest_error_service": str(worst["service"]),
        "highest_error_rate": round(float(worst["error_rate"]), 4),
        "sla_breach_rate": round(float(frame["latency_ms"].gt(latency_sla).mean()), 4),
        "output": str(output),
    }


def main() -> int:
    """Validate chart configuration, generate the dashboard, and print its audit summary."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path, default=Path("service_reliability_dashboard.png"))
    parser.add_argument("--latency-sla", type=float, default=260.0)
    args = parser.parse_args()
    try:
        if args.latency_sla <= 0:
            raise ValueError("--latency-sla must be positive")
        summary = make_dashboard(load_data(args.input), args.output, args.latency_sla)
        print(json.dumps(summary, indent=2))
        return 0
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        print(f"error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
