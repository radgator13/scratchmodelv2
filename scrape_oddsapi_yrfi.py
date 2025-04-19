import requests
import pandas as pd
from datetime import datetime
from pytz import timezone

API_KEY = "591b5b68a9802e9b588155794300ed47"
SPORT = "baseball_mlb"
REGION = "us"
MARKETS = "totals"  # closest thing to YRFI scoring environment
API_URL = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds/"

# === Get today in EST
eastern = timezone("US/Eastern")
today_est = datetime.now(eastern).strftime("%Y-%m-%d")

params = {
    "apiKey": API_KEY,
    "regions": REGION,
    "markets": MARKETS,
    "oddsFormat": "american",
    "dateFormat": "iso"
}

print(f"📡 Fetching MLB totals from The Odds API for {today_est}...")

response = requests.get(API_URL, params=params)
if response.status_code != 200:
    raise Exception(f"❌ API failed: {response.status_code} — {response.text}")

games = response.json()
rows = []

for game in games:
    try:
        away = game["away_team"]
        home = game["home_team"]
        start_time = game["commence_time"]

        # Extract total (O/U) from the first book that has it
        total = None
        for bookmaker in game["bookmakers"]:
            for market in bookmaker["markets"]:
                if market["key"] == "totals":
                    total = market["outcomes"][0]["point"]
                    break
            if total:
                break

        rows.append({
            "Game Date": today_est,
            "Away Team": away,
            "Home Team": home,
            "Total": total
        })
    except Exception as e:
        print(f"⚠️ Failed to parse game: {e}")
        continue

df = pd.DataFrame(rows)

if df.empty:
    print("❌ No totals found.")
else:
    print("\n✅ Totals (scoring proxies) pulled:")
    print(df)
    df.to_csv("data/yrfi_market_odds.csv", index=False)
    print("\n💾 Saved to data/yrfi_market_odds.csv")
