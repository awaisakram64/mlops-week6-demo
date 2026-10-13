"""
Builds reference.json: what good data looks like. Run once, on data you trust.

    python build_reference.py

reference.json is small, so Git versions it. The definition of "normal"
then has a history, just like the data.
"""
import json

import pandas as pd

df = pd.read_csv("data/loans.csv")

ref = {}
for col in ["income", "loan_amount", "credit_score"]:
    ref[col] = {"mean": round(float(df[col].mean()), 1),
                "null_rate": round(float(df[col].isna().mean()), 4),
                "min": int(df[col].min()), "max": int(df[col].max())}

with open("reference.json", "w") as f:
    json.dump(ref, f, indent=2)

print(f"reference.json written from {len(df):,} rows of data/loans.csv")
