import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime
import time

# === Load model artifacts ===
clf_ats = joblib.load("models/model_ats.pkl")
clf_total = joblib.load("models/model_total.pkl")
lb_ats = joblib.load("models/label_encoder_ats.pkl")
lb_total = joblib.load("models/label_encoder_total.pkl")
features_ats = joblib.load("models/trained_features_ats.pkl")
features_total = joblib.load("models/trained_features_total.pkl")

# === Load regression models for scores ===
reg_home = joblib.load("models/model_home_score.pkl")
reg_away = joblib.load("models/model_away_score.pkl")
features_home = joblib.load("models/trained_features_home_score.pkl")
features_away = joblib.load("models/trained_features_away_score.pkl")

# === Load input ===
df = pd.read_csv("data/mlb_model_and_odds.csv")

# 🔁 Prevent caching issues (slight delay)
time.sleep(0.5)

# === Patch missing scores from boxscores ===
print("🔄 Patching missing scores from mlb_boxscores_cleaned.csv...")

try:
    box = pd.read_csv("data/mlb_boxscores_cleaned.csv")

    # Normalize all merge keys
    for df_ in [df, box]:
        df_["Game Date"] = pd.to_datetime(df_["Game Date"], errors="coerce").dt.strftime("%Y-%m-%d")
        df_["Home Team"] = df_["Home Team"].astype(str).str.strip().str.title()
        df_["Away Team"] = df_["Away Team"].astype(str).str.strip().str.title()

    box = box[["Game Date", "Home Team", "Away Team", "Home Score", "Away Score"]]

    # Merge scores where missing
    df = df.merge(box, on=["Game Date", "Home Team", "Away Team"], how="left", suffixes=("", "_patch"))

    # Fill only missing scores
    df["Home Score"] = df["Home Score"].combine_first(df["Home Score_patch"])
    df["Away Score"] = df["Away Score"].combine_first(df["Away Score_patch"])
    df.drop(columns=["Home Score_patch", "Away Score_patch"], inplace=True)

    # Confirm merge worked
    april18 = df[df["Game Date"] == "2025-04-18"]
    print("\n📋 Post-merge April 18 scores:")
    print(april18[["Game Date", "Home Team", "Away Team", "Home Score", "Away Score"]].head())

except Exception as e:
    print(f"❌ Failed to patch scores: {e}")


# === DEBUG: Show April 18 records ===
print("\n📋 Checking for April 18 scores in input data:")
april18 = df[(df["Game Date"] == "2025-04-18") & df["Home Score"].notna()]
print(april18[["Game Date", "Home Team", "Away Team", "Home Score", "Away Score"]].head())

# === Feature engineering ===
if "ML Home" in df.columns and "ML Away" in df.columns:
    df["ML_Diff"] = df["ML Home"] - df["ML Away"]
    df["Log_Odds_Diff"] = np.where(
        df["ML Away"] != 0,
        np.log(df["ML Home"] / df["ML Away"]),
        np.nan
    )

if "Spread Home" in df.columns and "Spread Away" in df.columns:
    df["Spread_Diff"] = df["Spread Home"] - df["Spread Away"]

# Fill missing features with 0
for col in features_ats + features_total + features_home + features_away:
    if col not in df.columns:
        df[col] = 0

# === Predict ATS where possible ===
ats_rows = df.dropna(subset=features_ats)
X_ats = ats_rows[features_ats]
df.loc[ats_rows.index, "Model ATS Pick"] = lb_ats.inverse_transform(clf_ats.predict(X_ats))
df.loc[ats_rows.index, "ATS Confidence"] = clf_ats.predict_proba(X_ats).max(axis=1)

# === Predict Total where possible ===
total_rows = df.dropna(subset=features_total)
X_total = total_rows[features_total]
df.loc[total_rows.index, "Model Total Pick"] = lb_total.inverse_transform(clf_total.predict(X_total))
df.loc[total_rows.index, "Total Confidence"] = clf_total.predict_proba(X_total).max(axis=1)

# === Predict Home Score ===
home_rows = df.dropna(subset=features_home)
X_home = home_rows[features_home]
df.loc[home_rows.index, "Predicted Home Score"] = reg_home.predict(X_home)

# === Predict Away Score ===
away_rows = df.dropna(subset=features_away)
X_away = away_rows[features_away]
df.loc[away_rows.index, "Predicted Away Score"] = reg_away.predict(X_away)

# === Fireball ratings ===
def assign_fireballs(series):
    q = series.quantile([0.25, 0.5, 0.75, 0.95]).to_dict()
    return series.apply(lambda x: (
        "🔥🔥🔥🔥🔥" if x >= q[0.95] else
        "🔥🔥🔥🔥" if x >= q[0.75] else
        "🔥🔥🔥" if x >= q[0.5] else
        "🔥🔥" if x >= q[0.25] else
        "🔥"
    ))

if "ATS Confidence" in df.columns:
    df["ATS Fireballs"] = assign_fireballs(df["ATS Confidence"])

if "Total Confidence" in df.columns:
    df["Total Fireballs"] = assign_fireballs(df["Total Confidence"])

# === Save predictions ===
output_file = "data/mlb_predictions_all.csv"
df.to_csv(output_file, index=False)
print(f"✅ Saved predictions to {output_file} ({len(df)} rows)")
