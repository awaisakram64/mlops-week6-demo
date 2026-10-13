import json
import os
import pickle

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

FEATURES = ["income", "loan_amount", "credit_score"]

df = pd.read_csv("data/loans.csv")

X = df[FEATURES]
y = df["default"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

accuracy = model.score(X_test, y_test)
print(f"Accuracy: {accuracy * 100:.1f} %")

os.makedirs("models", exist_ok=True)
with open("models/model.pkl", "wb") as f:
    pickle.dump(model, f)
with open("metrics.json", "w") as f:
    json.dump({"accuracy": round(accuracy, 3)}, f, indent=2)
