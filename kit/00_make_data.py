"""
Generates every CSV used in the Week 6 demo.

Run it once, THE DAY BEFORE CLASS (not weeks before): the freshness check
compares application dates against today's date.

    python 00_make_data.py

Writes:
    data/loans.csv               version 1, 5,000 applicants (the starting data)
    batches/loans_v2.csv         version 2, 6,000 applicants (v1 plus 1,000 new)
    batches/loans_v3_good.csv    version 3, 7,000 applicants (v2 plus 1,000 new)
    batches/batch_new.csv        1,000 fresh, correct applicants (used by 04_make_batches.py)

Then run 04_make_batches.py to create the bad batches.
"""
import os
from datetime import date, timedelta

import numpy as np
import pandas as pd


def make_applicants(n, seed, newest_days_ago=0, spread_days=14):
    rng = np.random.default_rng(seed)

    income = np.clip(np.round(rng.lognormal(np.log(42_000), 0.45, n), -2), 12_000, 250_000)
    ratio = rng.lognormal(np.log(8), 0.45, n)
    loan_amount = np.clip(np.round(income * ratio, -3), 20_000, 2_500_000)
    credit_score = np.clip(np.round(rng.normal(650, 70, n)), 300, 850).astype(int)

    # Default risk rises with the loan-to-income ratio and falls with credit score.
    risk = (2.6 * (np.log(loan_amount / income) - np.log(8))
            - 0.03 * (credit_score - 650)
            + rng.normal(0, 0.55, n))
    default = (risk > 0.6).astype(int)

    today = date.today()
    days_ago = newest_days_ago + rng.integers(0, spread_days + 1, n)
    days_ago[0] = newest_days_ago          # make sure the newest date is exact
    application_date = [(today - timedelta(days=int(d))).isoformat() for d in days_ago]

    return pd.DataFrame({
        "income": income.astype(int),
        "loan_amount": loan_amount.astype(int),
        "credit_score": credit_score,
        "application_date": application_date,
        "default": default,
    })


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    os.makedirs("batches", exist_ok=True)

    v1 = make_applicants(5_000, seed=1)
    v2 = pd.concat([v1, make_applicants(1_000, seed=2)], ignore_index=True)
    v3 = pd.concat([v2, make_applicants(1_000, seed=3)], ignore_index=True)
    new = make_applicants(1_000, seed=4)

    v1.to_csv("data/loans.csv", index=False)
    v2.to_csv("batches/loans_v2.csv", index=False)
    v3.to_csv("batches/loans_v3_good.csv", index=False)
    new.to_csv("batches/batch_new.csv", index=False)

    for name, df in [("data/loans.csv", v1), ("batches/loans_v2.csv", v2),
                     ("batches/loans_v3_good.csv", v3), ("batches/batch_new.csv", new)]:
        print(f"{name:28s} {len(df):>6,} rows   default rate {df['default'].mean():.0%}")
