import pandas as pd
import joblib
import os

# === Paths ===
MODEL_PATH = "models/yrfi_pregame_model.pkl"
FEATURES_PATH = "data/yrfi_pregame_features_today.csv"
OUTPUT_PATH = "data/yrfi_predictions_pregame.csv"

# === Load model ===
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
model = joblib.load(MODEL_PATH)

# === Load features
df = pd.read_csv(FEATURES_PATH)
df["Game Date"] = pd.to_datetime(df["Game Date"])

# === Define model inputs
features = ["Away_YRFI_Rate", "Away_Avg_1st", "Home_YRFI_Rate", "Home_Avg_1st"]
df = df.dropna(subset=features)

# === Predict
df["YRFI_Prob"] = model.predict_proba(df[features])[:, 1]
df["NRFI_Prob"] = 1 - df["YRFI_Prob"]

# === Fireballs
def fireballs(p):
    if p >= 0.80: return "🔥🔥🔥🔥🔥"
    elif p >= 0.60: return "🔥🔥🔥🔥"
    elif p >= 0.40: return "🔥🔥🔥"
    elif p >= 0.20: return "🔥🔥"
    else: return "🔥"

df["YRFI🔥"] = df["YRFI_Prob"].apply(fireballs)
df["NRFI🔥"] = df["NRFI_Prob"].apply(fireballs)

# === Output columns
output_cols = [
    "Game Date", "Away Team", "Home Team",
    "Total" if "Total" in df.columns else None,
    "YRFI_Prob", "YRFI🔥", "NRFI_Prob", "NRFI🔥"
]
output_cols = [col for col in output_cols if col]

# === Sort and save
df[output_cols].sort_values("YRFI_Prob", ascending=False).to_csv(OUTPUT_PATH, index=False)
