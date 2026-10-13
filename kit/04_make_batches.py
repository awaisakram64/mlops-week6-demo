"""
Creates the bad batches for Parts 3, 4 and 5. Run after 00_make_data.py.

    python 04_make_batches.py

Every bad batch starts from correct data and breaks it in ONE realistic way,
so each check in the contract has exactly one thing to catch.

    batches/batch_renamed.csv    loan_amount renamed to loan_amt          -> schema
    batches/batch_string.csv     credit_score arrives as text             -> schema
    batches/batch_nullzero.csv   5% of incomes missing, filled with 0     -> schema (range)
    batches/batch_monthly.csv    income per month instead of per year     -> distribution
    batches/batch_swapped.csv    income and loan_amount swapped           -> distribution
    batches/batch_stale.csv      an old extract sent again                -> freshness
    batches/loans_bad.csv        the next full export (7,000 rows) with
                                 monthly income AND zeros for missing     -> Part 3 and Part 5
"""
import numpy as np
import pandas as pd

from importlib import import_module

make_applicants = import_module("00_make_data").make_applicants

rng = np.random.default_rng(42)
new = pd.read_csv("batches/batch_new.csv")


def save(df, name):
    df.to_csv(f"batches/{name}", index=False)
    print(f"batches/{name:20s} {len(df):>6,} rows")


# 1. Renamed column
save(new.rename(columns={"loan_amount": "loan_amt"}), "batch_renamed.csv")

# 2. A number arriving as text: the new export writes missing scores as "unknown"
df = new.copy()
df["credit_score"] = df["credit_score"].astype(str)
df.loc[rng.choice(len(df), 40, replace=False), "credit_score"] = "unknown"
save(df, "batch_string.csv")

# 3. Missing incomes filled with 0
df = new.copy()
df.loc[rng.choice(len(df), 50, replace=False), "income"] = 0
save(df, "batch_nullzero.csv")

# 4. Income per month instead of per year
df = new.copy()
df["income"] = (df["income"] / 12).round().astype(int)
save(df, "batch_monthly.csv")

# 5. income and loan_amount swapped (Week 1 Failure 4b, for a whole batch)
df = new.copy()
df[["income", "loan_amount"]] = df[["loan_amount", "income"]].values
save(df, "batch_swapped.csv")

# 6. A stale extract: correct values, but the newest row is 94 days old
save(make_applicants(1_000, seed=5, newest_days_ago=94, spread_days=30), "batch_stale.csv")

# 7. The next full export in the new format: monthly income, and zeros for missing
df = pd.read_csv("batches/loans_v3_good.csv")
df["income"] = (df["income"] / 12).round().astype(int)
df.loc[rng.choice(len(df), 312, replace=False), "income"] = 0
save(df, "loans_bad.csv")
