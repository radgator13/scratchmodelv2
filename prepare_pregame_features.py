import pandas as pd
from datetime import datetime

# === Load boxscore data
boxscores = pd.read_csv("data/mlb_boxscores_cleaned.csv")

# === Clean and ensure types
boxscores["Away 1st"] = pd.to_numeric(boxscores["Away 1st"], errors="coerce").fillna(0)
boxscores["Home 1st"] = pd.to_numeric(boxscores["Home 1st"], errors="coerce").fillna(0)
boxscores["YRFI"] = pd.to_numeric(boxscores["YRFI"], errors="coerce").fillna(0)
boxscores["Game Date"] = pd.to_datetime(boxscores["Game Date"])
boxscores["Away Team"] = boxscores["Away Team"].str.strip()
boxscores["Home Team"] = boxscores["Home Team"].str.strip()

# === Aggregate team stats
away_stats = boxscores.groupby("Away Team").agg(
    Away_YRFI_Rate=("YRFI", "mean"),
    Away_Avg_1st=("Away 1st", "mean")
).reset_index()

home_stats = boxscores.groupby("Home Team").agg(
    Home_YRFI_Rate=("YRFI", "mean"),
    Home_Avg_1st=("Home 1st", "mean")
).reset_index()

# === Build full list of known games
games = boxscores[["Game Date", "Away Team", "Home Team"]].drop_duplicates()

# === Load market odds
try:
    odds = pd.read_csv("data/yrfi_market_odds.csv")
    odds["Game Date"] = pd.to_datetime(odds["Game Date"])
    odds["Away Team"] = odds["Away Team"].str.strip()
    odds["Home Team"] = odds["Home Team"].str.strip()
except Exception as e:
    print(f"⚠️ Could not load odds: {e}")
    odds = pd.DataFrame()

# === Only use today's odds
today = datetime.now().date()
odds_today = odds[odds["Game Date"].dt.date == today].copy()

# === Combine matchups
all_games = pd.concat([games, odds_today[["Game Date", "Away Team", "Home Team"]]]).drop_duplicates()

# === Merge stats
df = all_games.merge(away_stats, on="Away Team", how="left")
df = df.merge(home_stats, on="Home Team", how="left")

# === Merge in totals for today
if not odds_today.empty:
    print(f"\n🔍 Merging {len(odds_today)} odds rows for today...")
    before_merge = df.copy()
    df = df.merge(
        odds_today[["Game Date", "Away Team", "Home Team", "Total"]],
        on=["Game Date", "Away Team", "Home Team"],
        how="left"
    )

    # Show what's missing after merge
    missing_totals = df[(df["Game Date"].dt.date == today) & (df["Total"].isna())]
    if not missing_totals.empty:
        print("\n⚠️ The following matchups had no Total merged:")
        print(missing_totals[["Game Date", "Away Team", "Home Team"]].to_string(index=False))
    else:
        print("✅ All today matchups got their Total values.")

# === Final cleanup
df = df.dropna(subset=["Away_YRFI_Rate", "Home_YRFI_Rate"])
df["Game Date"] = pd.to_datetime(df["Game Date"])
df = df.sort_values("Game Date")

# === Output columns
feature_cols = [
    "Game Date", "Away Team", "Home Team",
    "Away_YRFI_Rate", "Away_Avg_1st",
    "Home_YRFI_Rate", "Home_Avg_1st",
]

if "Total" in df.columns:
    feature_cols.append("Total")

df[feature_cols].to_csv("data/yrfi_pregame_features_today.csv", index=False)
print("\n✅ Final dataset saved to data/yrfi_pregame_features_today.csv")
