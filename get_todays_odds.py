import requests
import pandas as pd
from datetime import datetime
import pytz

API_KEY = "591b5b68a9802e9b588155794300ed47"
SPORT = "baseball_mlb"
REGION = "us"
MARKET = "totals"
API_URL = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds/"

# Get today's date in Eastern Time
eastern = pytz.timezone("US/Eastern")
today_est = datetime.now(eastern).strftime("%Y-%m-%d")

params = {
    "apiKey": API_KEY,
    "regions": REGION,
    "markets": "totals,h2h",
    "oddsFormat": "decimal",
    "dateFormat": "iso"
}

print(f"📡 Fetching MLB odds for {today_est} (EST)...")

response = requests.get(API_URL, params=params)
if response.status_code != 200:
    raise Exception(f"❌ API request failed: {response.status_code} — {response.text}")

games = response.json()
rows = []

for game in games:
    try:
        home_team = game["home_team"]
        away_team = game["away_team"]
        commence_time = game["commence_time"]

        # Get totals (O/U)
        total = None
        for bookmaker in game["bookmakers"]:
            for market in bookmaker["markets"]:
                if market["key"] == "totals":
                    total = market["outcomes"][0]["point"]
                    break

        rows.append({
            "Game Date": today_est,
            "Away Team": away_team,
            "Home Team": home_team,
            "Start Time (ET)": commence_time,
            "Total": total
        })

    except Exception as e:
        print(f"⚠️ Failed to parse game: {e}")

# Save to CSV
odds_df = pd.DataFrame(rows)
odds_df.to_csv("data/mlb_odds_today.csv", index=False)
print("✅ Saved to data/mlb_odds_today.csv")
