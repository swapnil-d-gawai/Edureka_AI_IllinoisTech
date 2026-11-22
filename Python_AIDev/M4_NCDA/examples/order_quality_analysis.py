"""Clean and reconcile order and warehouse data with NumPy and pandas."""

from __future__ import annotations

from pathlib import Path
import argparse
import json

import numpy as np
import pandas as pd


def sample_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build a repeatable lesson dataset with invalid, duplicate, and unmatched rows."""
    orders = pd.DataFrame(
        [
            ("O-101", "SKU-A", 4, 12.5, "east"),
            ("O-102", "SKU-B", 2, 8.0, "west"),
            ("O-103", "SKU-A", -1, 12.5, "east"),
            ("O-104", "SKU-C", 3, 15.0, "north"),
            ("O-102", "SKU-B", 2, 8.0, "west"),
            ("O-105", "SKU-D", 5, 9.5, "south"),
        ],
        columns=["order_id", "sku", "quantity", "unit_price", "region"],
    )
    warehouse = pd.DataFrame(
        [
            ("SKU-A", 100, 1.0),
            ("SKU-B", 20, 0.8),
            ("SKU-C", 4, 1.1),
        ],
        columns=["sku", "available", "shipping_cost"],
    )
    return orders, warehouse


def load_csv(path: Path, required: set[str]) -> pd.DataFrame:
    """Load a CSV only after verifying the columns required by the mapping."""
    frame = pd.read_csv(path)
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"{path} missing columns: {sorted(missing)}")
    return frame


def analyze(orders: pd.DataFrame, warehouse: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    """Quarantine quality failures, enrich orders, and calculate decision metrics."""
    # Keep raw input unchanged; a copied transformation frame makes the cleaning boundary clear.
    numeric = orders.assign(
        quantity=pd.to_numeric(orders["quantity"], errors="coerce"),
        unit_price=pd.to_numeric(orders["unit_price"], errors="coerce"),
    )
    complete_mask = numeric[["order_id", "sku", "quantity", "unit_price"]].notna().all(axis=1)
    business_mask = (
        numeric["order_id"].astype(str).str.strip().ne("")
        & numeric["sku"].astype(str).str.strip().ne("")
        & numeric["quantity"].ge(1)
        & numeric["unit_price"].ge(0)
    )
    valid_mask = complete_mask & business_mask
    valid = numeric[valid_mask].copy()
    invalid_count = int((~valid_mask).sum())
    duplicate = valid[valid.duplicated("order_id", keep="first")]
    valid = valid.drop_duplicates("order_id", keep="first")

    # Cardinality validation prevents a duplicated warehouse key from multiplying transaction rows.
    merged = valid.merge(warehouse, on="sku", how="left", validate="many_to_one", indicator=True)
    unmatched = int(merged["_merge"].ne("both").sum())
    merged["gross_value"] = (merged["quantity"].to_numpy() * merged["unit_price"].to_numpy()).round(2)
    merged["fulfillable"] = np.logical_and(
        merged["_merge"].eq("both"), merged["quantity"].le(merged["available"].fillna(-1))
    )
    region_summary = (
        merged.groupby("region", dropna=False)
        .agg(order_count=("order_id", "nunique"), gross_value=("gross_value", "sum"), fill_rate=("fulfillable", "mean"))
        .reset_index()
    )
    report = {
        "input_rows": int(len(orders)),
        "valid_orders": int(len(valid)),
        "invalid_rows": int(max(invalid_count, 0)),
        "duplicate_rows": int(len(duplicate)),
        "unmatched_skus": unmatched,
        "gross_value": round(float(merged["gross_value"].sum()), 2),
        "fulfillable_rate": (
            round(float(merged["fulfillable"].mean()), 4) if not merged.empty else None
        ),
        "regions": region_summary.to_dict(orient="records"),
    }
    return merged.drop(columns="_merge"), report


def main() -> int:
    """Choose sample or file inputs and write both detailed and summary outputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--orders", type=Path)
    parser.add_argument("--warehouse", type=Path)
    parser.add_argument("--output", type=Path, default=Path("order_analysis.json"))
    args = parser.parse_args()
    try:
        if bool(args.orders) != bool(args.warehouse):
            raise ValueError("--orders and --warehouse must be supplied together")
        if args.orders and args.warehouse:
            orders = load_csv(args.orders, {"order_id", "sku", "quantity", "unit_price", "region"})
            warehouse = load_csv(args.warehouse, {"sku", "available", "shipping_cost"})
        else:
            orders, warehouse = sample_data()
        enriched, report = analyze(orders, warehouse)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        enriched.to_csv(args.output.with_suffix(".csv"), index=False)
        print(json.dumps(report, indent=2))
        return 0
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        print(f"error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
