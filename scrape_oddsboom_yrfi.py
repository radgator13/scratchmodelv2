import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from pytz import timezone

# === Config
URL = "https://oddsboom.com/mlb"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

print("🌐 Fetching OddsBoom MLB page...")
response = requests.get(URL, headers=HEADERS)

if response.status_code != 200:
    raise Exception(f"❌ Failed to load OddsBoom: {response.status_code}")

soup = BeautifulSoup(response.content, "html.parser")

# === Find prop blocks that contain YRFI/NRFI
print("🔍 Scanning page for YRFI props...")

rows = soup.find_all("div", class_="odd-row")
games = []

for row in rows:
    try:
        title_div = row.find("div", class_="odd-title")
        if not title_div or "1st Inning" not in title_div.text:
            continue

        matchup = row.find("div", class_="odd-matchup")
        if not matchup:
            continue

        teams = matchup.text.strip().split(" @ ")
        if len(teams) != 2:
            continue

        away_team, home_team = teams

        # Find books and prices
        book_blocks = row.find_all("div", class_="odd-book")
        for book in book_blocks:
            book_name = book.find("div", class_="odd-book-name").text.strip()
            odds = book.find_all("div", class_="odd-number")
            if len(odds) < 2:
                continue

            yrfi = odds[0].text.strip().replace("+", "").replace("−", "-")
            nrfi = odds[1].text.strip().replace("+", "").replace("−", "-")

            games.append({
                "Game Date": datetime.now(timezone("US/Eastern")).strftime("%Y-%m-%d"),
                "Away Team": away_team,
                "Home Team": home_team,
                "Book": book_name,
                "YRFI Odds": int(yrfi),
                "NRFI Odds": int(nrfi)
            })

    except Exception as e:
        print(f"⚠️ Error parsing row: {e}")
        continue

# === Output
df = pd.DataFrame(games)
if df.empty:
    print("❌ No props found. Try again later.")
else:
    print("\n✅ YRFI props scraped from OddsBoom:")
    print(df)
    df.to_csv("data/yrfi_market_odds.csv", index=False)
    print("\n💾 Saved to data/yrfi_market_odds.csv")
