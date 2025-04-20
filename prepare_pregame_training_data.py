import pandas as pd

# === Load boxscore data ===
df = pd.read_csv("data/mlb_boxscores_cleaned.csv")

# === Clean and ensure numeric types ===
df["Away 1st"] = pd.to_numeric(df["Away 1st"], errors="coerce").fillna(0)
df["Home 1st"] = pd.to_numeric(df["Home 1st"], errors="coerce").fillna(0)
df["YRFI"] = pd.to_numeric(df["YRFI"], errors="coerce").fillna(0)

# === Calculate team stats up to each game date ===
def rolling_stats(df, team_col, score_col, outcome_col, label_prefix):
    stats = (
        df
        .sort_values("Game Date")
        .groupby(team_col)
        .rolling(window=10, min_periods=3, on="Game Date")[[score_col, outcome_col]]
        .mean()
        .reset_index()
        .rename(columns={
            score_col: f"{label_prefix}_Avg_1st",
            outcome_col: f"{label_prefix}_YRFI_Rate"
        })
    )
    return stats

away_stats = rolling_stats(df, "Away Team", "Away 1st", "YRFI", "Away")
home_stats = rolling_stats(df, "Home Team", "Home 1st", "YRFI", "Home")

# === Merge back to full dataset ===
df = df.merge(away_stats, on=["Away Team", "Game Date"], how="left")
df = df.merge(home_stats, on=["Home Team", "Game Date"], how="left")

# === Drop rows without enough history
df = df.dropna(subset=["Away_YRFI_Rate", "Away_Avg_1st", "Home_YRFI_Rate", "Home_Avg_1st"])

# === Select final training columns
final_cols = [
    "Game Date", "Away Team", "Home Team",
    "Away_YRFI_Rate", "Away_Avg_1st",
    "Home_YRFI_Rate", "Home_Avg_1st",
    "YRFI"
]

df[final_cols].to_csv("data/yrfi_training_pregame.csv", index=False)
print("✅ Training data saved to data/yrfi_training_pregame.csv")
