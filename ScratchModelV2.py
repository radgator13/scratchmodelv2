import os
import pandas as pd
from datetime import datetime

# Step 1: Scrape updated box scores (includes today + tomorrow if get_scores.py is patched)
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

# Merge in totals if available
if os.path.exists("data/yrfi_market_odds.csv"):
    totals = pd.read_csv("data/yrfi_market_odds.csv")
    df = pd.merge(df, totals, on=["Game Date", "Away Team", "Home Team"], how="left")

# Add NRFI probability and 🔥 tiers
df["NRFI_Prob"] = 1 - df["YRFI_Prob"]

def to_fireballs(p):
    if p >= 0.80: return "🔥🔥🔥🔥🔥"
    elif p >= 0.60: return "🔥🔥🔥🔥"
    elif p >= 0.40: return "🔥🔥🔥"
    elif p >= 0.20: return "🔥🔥"
    else: return "🔥"

df["YRFI🔥"] = df["YRFI_Prob"].apply(to_fireballs)
df["NRFI🔥"] = df["NRFI_Prob"].apply(to_fireballs)

# Define columns to save
output_cols = ["Game Date", "Away Team", "Home Team", "YRFI_Prob", "YRFI🔥", "NRFI_Prob", "NRFI🔥"]
if "Total" in df.columns:
    output_cols.append("Total")

# Save to dashboard + archive
df = df.sort_values(by="Game Date")
df[output_cols].to_csv("data/yrfi_predictions_pregame.csv", index=False)
df[output_cols].to_csv("data/yrfi_value_targets.csv", index=False)

print("\n✅ Done! All predictions updated with fireballs in:")
print("   📁 data/yrfi_predictions_pregame.csv")
print("   📁 data/yrfi_value_targets.csv")

# Step 7: Commit and push updated files to GitHub
print("📤 Step 7: Committing and pushing updates to GitHub...")
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Step 7a: Force a change to ensure there's always something to commit
touch_file = "data/.last_push.txt"
with open(touch_file, "w") as f:
    f.write(f"Last pushed at {timestamp}\n")

# Step 7b: Add all relevant files (data, scripts, dashboard, etc.)
os.system("git add data/*.csv data/.last_push.txt *.py *.md *.bat")

# Step 7c: Commit with timestamped message
os.system(f'git commit -m "🤖 Auto update @ {timestamp}"')

# Step 7d: Push to GitHub
os.system("git push origin main")



# # Step 8: Launch Streamlit dashboard
# print("🚀 Step 8: Launching Streamlit dashboard...")
# os.system("start streamlit run yrfi_dashboard.py")
