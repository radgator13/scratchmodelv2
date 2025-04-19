import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# === Page setup ===
st.set_page_config(page_title="YRFI Dashboard", layout="wide")
st.title("🔥 YRFI/NRFI Prediction Dashboard")

# === Load predictions and results ===
preds = pd.read_csv("data/yrfi_predictions_pregame.csv")
box = pd.read_csv("data/mlb_boxscores_cleaned.csv")

preds["Game Date"] = pd.to_datetime(preds["Game Date"])
box["Game Date"] = pd.to_datetime(box["Game Date"])

# === Merge predictions with actual YRFI outcome ===
merged = preds.merge(
    box[["Game Date", "Away Team", "Home Team", "YRFI"]],
    on=["Game Date", "Away Team", "Home Team"],
    how="left"
)

# === Add hit/miss indicator ===
def outcome_check(row):
    if pd.isna(row["YRFI"]):
        return "❓"
    correct = (
        (row["YRFI_Prob"] >= 0.5 and row["YRFI"] == 1) or
        (row["YRFI_Prob"] < 0.5 and row["YRFI"] == 0)
    )
    return "✅" if correct else "❌"

merged["Correct"] = merged.apply(outcome_check, axis=1)

# === Calendar ===
min_date = merged["Game Date"].min().date()
max_date = merged["Game Date"].max().date()
selected_date = st.date_input("📅 Select Game Date", value=max_date, min_value=min_date, max_value=datetime.today().date())

# === Filter by selected date ===
filtered = merged[merged["Game Date"].dt.date == selected_date]

# === Show predictions ===
if not filtered.empty:
    st.subheader(f"Games for {selected_date.strftime('%Y-%m-%d')}")

    # Build display columns dynamically
    cols = ["Away Team", "Home Team", "YRFI_Prob"]
    if "YRFI🔥" in filtered.columns: cols.append("YRFI🔥")
    if "NRFI_Prob" in filtered.columns: cols.append("NRFI_Prob")
    if "NRFI🔥" in filtered.columns: cols.append("NRFI🔥")
    if "Total" in filtered.columns: cols.append("Total")
    if "YRFI" in filtered.columns: cols.append("YRFI")
    if "Correct" in filtered.columns: cols.append("Correct")

    # De-duplicate columns
    seen = set()
    deduped_cols = [c for c in cols if not (c in seen or seen.add(c))]

    st.dataframe(filtered[deduped_cols], use_container_width=True)
else:
    st.warning("No predictions found for this date.")

# === Accuracy summary ===
today_total = filtered.shape[0]
today_correct = (filtered["Correct"] == "✅").sum()
today_wrong = (filtered["Correct"] == "❌").sum()

cumulative = merged[merged["Game Date"].dt.date <= selected_date]
cumulative_total = cumulative.shape[0]
cumulative_correct = (cumulative["Correct"] == "✅").sum()
cumulative_wrong = (cumulative["Correct"] == "❌").sum()

st.markdown("---")
st.subheader("📊 Prediction Accuracy Summary")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📅 Daily Accuracy")
    st.metric("Correct", today_correct)
    st.metric("Incorrect", today_wrong)
    st.metric("Total Predictions", today_total)

with col2:
    st.markdown("#### 📈 Cumulative Accuracy (Up to Selected Date)")
    st.metric("Correct", cumulative_correct)
    st.metric("Incorrect", cumulative_wrong)
    st.metric("Total Predictions", cumulative_total)

# === Fireball Tier Breakdown
st.markdown("---")
st.subheader("🔥 Fireball Tier Performance Breakdown")

# Define tier order and filter only valid flame rows
tiers = ["🔥", "🔥🔥", "🔥🔥🔥", "🔥🔥🔥🔥", "🔥🔥🔥🔥🔥"]
fire_df = merged[merged["YRFI🔥"].isin(tiers)]
fire_df = fire_df[fire_df["Game Date"].dt.date <= selected_date]

# Group by fireball strength
tier_stats = (
    fire_df.groupby("YRFI🔥")["Correct"]
    .value_counts()
    .unstack(fill_value=0)
    .rename(columns={"✅": "Correct", "❌": "Incorrect"})
)

tier_stats["Total"] = tier_stats["Correct"] + tier_stats["Incorrect"]
tier_stats["Accuracy %"] = (tier_stats["Correct"] / tier_stats["Total"] * 100).round(1)
tier_stats = tier_stats.reindex(tiers).fillna(0).astype({"Correct": int, "Incorrect": int, "Total": int})

st.dataframe(tier_stats, use_container_width=True)
# === Fireball Daily Performance Chart
# === Fireball Summary (Prediction-Style)
# === Compact Fireball Accuracy Summary
st.markdown("---")
st.subheader("🔥 Fireball Accuracy Summary (Compact View)")

tiers = ["🔥🔥🔥🔥🔥", "🔥🔥🔥🔥", "🔥🔥🔥", "🔥🔥", "🔥"]


def summarize_fireballs(df):
    result = {}
    for tier in tiers:
        subset = df[df["YRFI🔥"] == tier]
        correct = (subset["Correct"] == "✅").sum()
        incorrect = (subset["Correct"] == "❌").sum()
        total = correct + incorrect
        result[tier] = {"Correct": correct, "Incorrect": incorrect, "Total": total}
    return result

daily_stats = summarize_fireballs(filtered)
rolling_stats = summarize_fireballs(cumulative)

# Build summary DataFrame
rows = []
for tier in tiers:
    row = {
        "Tier": tier,
        "Daily Correct": daily_stats[tier]["Correct"],
        "Daily Incorrect": daily_stats[tier]["Incorrect"],
        "Daily Total": daily_stats[tier]["Total"],
        "Rolling Correct": rolling_stats[tier]["Correct"],
        "Rolling Incorrect": rolling_stats[tier]["Incorrect"],
        "Rolling Total": rolling_stats[tier]["Total"],
    }
    rows.append(row)

summary_df = pd.DataFrame(rows)
st.dataframe(summary_df.set_index("Tier"), use_container_width=True)

