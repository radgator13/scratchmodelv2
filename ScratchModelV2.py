import os
import pandas as pd
from datetime import datetime

# Step 1: Scrape updated box scores
print("📦 Step 1: Running get_scores.py...")
os.system("python get_scores.py")

# Step 2: Rebuild training data
print("📦 Step 2: Building training set...")
os.system("python prepare_pregame_training_data.py")

# Step 3: Train the model
print("📦 Step 3: Training pregame model...")
os.system("python train_pregame_yrfi_model.py")

# Step 4: Prepare features for all known matchups
print("📦 Step 4: Preparing features...")
os.system("python prepare_pregame_features.py")

# Step 5: Predict YRFI on all available matchups
print("📦 Step 5: Generating model predictions...")
os.system("python predict_yrfi_pregame.py")

# Step 6: Merge with totals and add fireballs
print("📦 Step 6: Enhancing predictions with totals + fireballs...")

# Load latest predictions
df = pd.read_csv("data/yrfi_predictions_pregame.csv")

# Add totals if they exist
if os.path.exists("data/yrfi_market_odds.csv"):
    totals = pd.read_csv("data/yrfi_market_odds.csv")
    df = pd.merge(df, totals, on=["Game Date", "Away Team", "Home Team"], how="left")

# Add NRFI and fireball columns
df["NRFI_Prob"] = 1 - df["YRFI_Prob"]

def to_fireballs(p):
    if p >= 0.80: return "🔥🔥🔥🔥🔥"
    elif p >= 0.60: return "🔥🔥🔥🔥"
    elif p >= 0.40: return "🔥🔥🔥"
    elif p >= 0.20: return "🔥🔥"
    else: return "🔥"

df["YRFI🔥"] = df["YRFI_Prob"].apply(to_fireballs)
df["NRFI🔥"] = df["NRFI_Prob"].apply(to_fireballs)

# Output columns
output_cols = ["Game Date", "Away Team", "Home Team", "YRFI_Prob", "YRFI🔥", "NRFI_Prob", "NRFI🔥"]
if "Total" in df.columns:
    output_cols.append("Total")

# Sort and save to both required files
df = df.sort_values(by="Game Date")
df[output_cols].to_csv("data/yrfi_predictions_pregame.csv", index=False)      # LIVE predictions for dashboard
df[output_cols].to_csv("data/yrfi_value_targets.csv", index=False)            # Historical full view (if needed)

print("\n✅ Done! All predictions updated with fireballs in:")
print("   📁 data/yrfi_predictions_pregame.csv")
print("   📁 data/yrfi_value_targets.csv")
