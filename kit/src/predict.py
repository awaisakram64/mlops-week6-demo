"""
Scores one loan applicant with models/model.pkl.

    python src/predict.py                  the Week 1 applicant
    python src/predict.py swapped          income and loan_amount swapped
    python src/predict.py swapped nocheck  skip the check (the Week 1 behaviour)

The request is checked against reference.json once that file exists (Part 4).
Before then, there is nothing to check against, so the model answers anything.
"""
import os
import json
import pickle
import sys

import pandas as pd

APPLICANTS = {
    "good":    {"income": 48000,  "loan_amount": 420000, "credit_score": 560},
    "swapped": {"income": 420000, "loan_amount": 48000,  "credit_score": 560},
}


def validate_request(applicant, ref):
    for col, r in ref.items():
        v = applicant.get(col)
        if v is None:
            raise ValueError(f"missing field: {col}")
        if not isinstance(v, (int, float)):
            raise ValueError(f"{col}: expected a number")
        if not r["min"] <= v <= r["max"]:
            raise ValueError(f"{col}={v:,} is outside the training range "
                             f"{r['min']:,} to {r['max']:,}")


which = "swapped" if "swapped" in sys.argv else "good"
applicant = APPLICANTS[which]

if "nocheck" not in sys.argv and os.path.exists("reference.json"):
    with open("reference.json") as f:
        ref = json.load(f)
    try:
        validate_request(applicant, ref)
    except ValueError as e:
        print(f"REJECTED:    {e}")
        sys.exit(1)

with open("models/model.pkl", "rb") as f:
    model = pickle.load(f)

p_default = model.predict_proba(pd.DataFrame([applicant]))[0][1]
print("Prediction: ", "WILL DEFAULT" if p_default >= 0.5 else "will repay")
print(f"Confidence:  {p_default * 100:.1f}%")
