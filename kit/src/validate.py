"""
The data contract for loans.csv: schema, distribution and freshness.

    python src/validate.py data/loans.csv            all three checks on one file
    python src/validate.py data/loans.csv schema     the schema check only
    python src/validate.py data/loans.csv batches/*.csv   several files, summary table

Exit code 0 means every check passed. Exit code 1 means at least one failed,
which is what stops `dvc repro` when this script is a pipeline stage.
"""
import json
import os
import sys
from datetime import date

import pandas as pd

# ---------------------------------------------------------------- schema
SCHEMA = {
    "income":       {"min": 1,   "max": 10_000_000},
    "loan_amount":  {"min": 1,   "max": 50_000_000},
    "credit_score": {"min": 300, "max": 850},
    "default":      {"min": 0,   "max": 1},
}


def check_schema(df):
    errors = []
    for col, rule in SCHEMA.items():
        if col not in df.columns:
            errors.append(f"missing column: {col}"); continue
        if not pd.api.types.is_numeric_dtype(df[col]):
            errors.append(f"{col}: expected a number, got {df[col].dtype}"); continue
        if df[col].isna().any():
            errors.append(f"{col}: {df[col].isna().sum()} nulls")
        out = df[(df[col] < rule["min"]) | (df[col] > rule["max"])]
        if len(out):
            errors.append(f"{col}: {len(out)} rows outside {rule['min']:,} to {rule['max']:,}")
    return errors


# ---------------------------------------------------------- distribution
def check_distribution(df, ref, tolerance=0.25):
    errors = []
    for col, r in ref.items():
        mean = df[col].mean()
        if abs(mean - r["mean"]) > tolerance * r["mean"]:
            errors.append(f"{col}: mean {mean:,.0f} vs reference {r['mean']:,.0f}")
        if df[col].isna().mean() > r["null_rate"] + 0.02:
            errors.append(f"{col}: null rate {df[col].isna().mean():.0%}")
    return errors


# ------------------------------------------------------------- freshness
def check_freshness(df, max_age_days=30):
    if "application_date" not in df.columns:
        return ["missing column: application_date"]
    newest = pd.to_datetime(df["application_date"]).max().date()
    age = (date.today() - newest).days
    if age > max_age_days:
        return [f"newest row is {age} days old, limit {max_age_days}"]
    return []


# ------------------------------------------------------------ run checks
def run_checks(path, only_schema=False):
    """Returns {check name: list of errors, or None if the check did not run}."""
    df = pd.read_csv(path)
    results = {"SCHEMA": check_schema(df)}
    if only_schema:
        return results
    if results["SCHEMA"]:
        # A file with the wrong shape has no meaningful mean or date.
        results["DISTRIBUTION"] = None
        results["FRESHNESS"] = None
        return results
    with open("reference.json") as f:
        ref = json.load(f)
    results["DISTRIBUTION"] = check_distribution(df, ref)
    results["FRESHNESS"] = check_freshness(df)
    return results


def failed(results):
    return any(errors for errors in results.values())


def print_one(results):
    for check, errors in results.items():
        if errors is None:
            print(f"{check:13s} not run (schema failed)")
        elif not errors:
            print(f"{check:13s} PASS")
        else:
            print(f"{check:13s} FAIL  {errors[0]}")
            for e in errors[1:]:
                print(f"{'':13s}       {e}")


def label(errors):
    return "not run" if errors is None else ("FAIL" if errors else "PASS")


if __name__ == "__main__":
    args = sys.argv[1:]
    only_schema = "schema" in args
    files = [a for a in args if a != "schema"]

    if len(files) == 1:
        results = run_checks(files[0], only_schema)
        print_one(results)
        os.makedirs("reports", exist_ok=True)
        with open("reports/validation.json", "w") as f:
            json.dump({"file": files[0], "results": results}, f, indent=2)
        sys.exit(1 if failed(results) else 0)

    # Several files: one summary line each.
    print(f"{'FILE':24s} {'SCHEMA':8s} {'DISTRIBUTION':14s} FRESHNESS")
    any_failed = False
    for path in files:
        r = run_checks(path, only_schema)
        any_failed = any_failed or failed(r)
        print(f"{os.path.basename(path):24s} {label(r['SCHEMA']):8s} "
              f"{label(r.get('DISTRIBUTION')):14s} {label(r.get('FRESHNESS'))}")
    sys.exit(1 if any_failed else 0)
