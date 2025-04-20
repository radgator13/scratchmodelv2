import requests
import pandas as pd
from datetime import datetime
from pytz import timezone

API_KEY = "591b5b68a9802e9b588155794300ed47"
SPORT = "baseball_mlb"
REGION = "us"
MARKETS = "yes_run_in_1st_inning"
BOOK = "draftkings"  # You can adjust this if needed

# === Load model predictions ===
preds = pd.read_csv("data/yrfi_predictions_pregame.csv")

# === Get today's date in EST ===
eastern = timezone("US/Eastern")
today = datetime.now(eastern).strftime("%Y-%m-%d")

print(f"📡 Fetching props for {today}...")

url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds/"
params = {
    "apiKey": API_KEY,
    "regions": REGION,
    "markets": MARKETS,
    "oddsFormat": "american",
    "bookmakers": BOOK,
}

response = requests.get(url, params=params)
if response.status_code != 200:
    raise Exception(f"❌ API request failed: {response.status_code} — {response.text}")

games = response.json()
rows = []

def moneyline_to_prob(odds):
    odds = int(odds)
    return 100 / (odds + 100) if odds > 0 else abs(odds) / (abs(odds) + 100)

for game in games:
    try:
        home = game["home_team"]
        away = game["away_team"]
        date = game["commence_time"][:10]

        # Only look at games today
        if date != today:
            continue

        for bookmaker in game["bookmakers"]:
            for market in bookmaker["markets"]:
                if market["key"] == "yes_run_in_1st_inning":
                    for outcome in market["outcomes"]:
                        if outcome["name"] == "Yes":
                            yrfi_odds = outcome["price"]
                        elif outcome["name"] == "No":
                            nrfi_odds = outcome["price"]

        rows.append({
            "Game Date": date,
            "Away Team": away,
            "Home Team": home,
            "YRFI Odds": yrfi_odds,
            "NRFI Odds": nrfi_odds
        })

    except Exception as e:
        print(f"⚠️ Error parsing game: {e}")

# === Compare with model predictions ===
odds_df = pd.DataFrame(rows)
merged = preds.merge(odds_df, on=["Game Date", "Away Team", "Home Team"], how="inner")

# === Calculate Implied Probabilities and EV
merged["Market_YRFI_Prob"] = merged["YRFI Odds"].apply(moneyline_to_prob)
merged["Model_EV"] = (
    merged["YRFI_Prob"] * (merged["YRFI Odds"].apply(lambda x: abs(x) / 100 if x > 0 else 100 / abs(x)))
    - (1 - merged["YRFI_Prob"])
)

# === Output top value bets
print("\n💰 Top +EV YRFI Opportunities:\n")
top = merged.sort_values("Model_EV", ascending=False)[
    ["Game Date", "Away Team", "Home Team", "YRFI_Prob", "YRFI Odds", "Market_YRFI_Prob", "Model_EV"]
]
print(top.to_string(index=False))

top.to_csv("data/yrfi_value_bets.csv", index=False)
print("\n✅ Saved to data/yrfi_value_bets.csv")
