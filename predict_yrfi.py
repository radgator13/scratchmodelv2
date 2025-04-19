import pandas as pd
import joblib
import os
from datetime import datetime
from pytz import timezone

# === Config ===
MODEL_PATH = "models/yrfi_model.pkl"
DATA_PATH = "data/mlb_boxscores_cleaned.csv"

# === Load model ===
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model not found at {MODEL_PATH}")

model = joblib.load(MODEL_PATH)

# === Load data ===
df = pd.read_csv(DATA_PATH)

# === Get today's date in Eastern Time ===
eastern = timezone('US/Eastern')
today_est = datetime.now(eastern).strftime("%Y-%m-%d")

df_today = df[df["Game Date"] == today_est].copy()

if df_today.empty:
    print(f"⚠️ No games found for EST date {today_est}. Showing latest available instead.")
    latest_date = df["Game Date"].max()
    df_today = df[df["Game Date"] == latest_date].copy()

# === Feature Engineering (same as training script) ===
df_today["Away 1st"] = pd.to_numeric(df_today["Away 1st"], errors="coerce").fillna(0)
df_today["Home 1st"] = pd.to_numeric(df_today["Home 1st"], errors="coerce").fillna(0)

df_today["Away Avg 1st"] = df_today.groupby("Away Team")["Away 1st"].transform("mean")
df_today["Home Avg 1st"] = df_today.groupby("Home Team")["Home 1st"].transform("mean")

features = ["Away Avg 1st", "Home Avg 1st"]
X = df_today[features]

# === Predict ===
df_today["YRFI_Prob"] = model.predict_proba(X)[:, 1]

# === Display Results ===
output_cols = ["Game Date", "Away Team", "Home Team", "YRFI_Prob"]
print("\n🎯 YRFI Predictions:\n")
print(df_today[output_cols].sort_values("YRFI_Prob", ascending=False).to_string(index=False))

# Optional: Save predictions
df_today[output_cols].to_csv("data/yrfi_predictions_today.csv", index=False)
print("\n✅ Predictions saved to data/yrfi_predictions_today.csv")
