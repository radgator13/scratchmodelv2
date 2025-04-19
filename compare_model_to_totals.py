import pandas as pd

# === Load model + market ===
model = pd.read_csv("data/yrfi_predictions_pregame.csv")
market = pd.read_csv("data/yrfi_market_odds.csv")

df = pd.merge(model, market, on=["Game Date", "Away Team", "Home Team"], how="inner")
df.rename(columns=lambda x: x.strip(), inplace=True)

# Clean column name
if "Total_y" in df.columns:
    df.rename(columns={"Total_y": "Total"}, inplace=True)

# === Add NRFI probability
df["NRFI_Prob"] = 1 - df["YRFI_Prob"]

# === Add fireball columns
def prob_to_fireballs(p):
    if p >= 0.80: return "🔥🔥🔥🔥🔥"
    elif p >= 0.60: return "🔥🔥🔥🔥"
    elif p >= 0.40: return "🔥🔥🔥"
    elif p >= 0.20: return "🔥🔥"
    else: return "🔥"

df["YRFI🔥"] = df["YRFI_Prob"].apply(prob_to_fireballs)
df["NRFI🔥"] = df["NRFI_Prob"].apply(prob_to_fireballs)

# === Sort and output
df_sorted = df.sort_values(by="YRFI_Prob", ascending=False)
cols = ["Game Date", "Away Team", "Home Team", "YRFI_Prob", "YRFI🔥", "NRFI_Prob", "NRFI🔥", "Total"]

print("\n🎯 YRFI/NRFI Fireball Ratings:\n")
print(df_sorted[cols].to_string(index=False))

df_sorted[cols].to_csv("data/yrfi_value_targets.csv", index=False)
print("\n💾 Saved with fireball ratings to data/yrfi_value_targets.csv")
