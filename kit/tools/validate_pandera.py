"""
OVERFLOW X1: the same schema rules written with pandera instead of plain pandas.

    pip install pandera
    python tools/validate_pandera.py batches/batch_nullzero.csv
"""
import sys

import pandas as pd
import pandera.pandas as pa

schema = pa.DataFrameSchema({
    "income":       pa.Column(int, pa.Check.in_range(1, 10_000_000)),
    "loan_amount":  pa.Column(int, pa.Check.in_range(1, 50_000_000)),
    "credit_score": pa.Column(int, pa.Check.in_range(300, 850)),
    "default":      pa.Column(int, pa.Check.isin([0, 1])),
})

df = pd.read_csv(sys.argv[1])
try:
    schema.validate(df, lazy=True)
    print("SCHEMA        PASS")
except pa.errors.SchemaErrors as e:
    print("SCHEMA        FAIL")
    print(e.failure_cases[["column", "check", "failure_case"]].head(5).to_string(index=False))
    sys.exit(1)
