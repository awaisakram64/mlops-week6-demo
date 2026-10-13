"""
A quick look at the income column of a CSV (Part 3, slide 66).

    python tools/peek.py data/loans.csv
"""
import sys

import pandas as pd

df = pd.read_csv(sys.argv[1])
income = df["income"]
print(f"rows      {len(df):>10,}")
print(f"mean      {income.mean():>10,.0f}")
print(f"min       {income.min():>10,}")
print(f"max       {income.max():>10,}")
print(f"zeros     {(income == 0).sum():>10,}")
