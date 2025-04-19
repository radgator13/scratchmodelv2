import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime
from pytz import timezone

# === Setup headless browser ===
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options)
url = "https://sportsbook.draftkings.com/leagues/baseball/mlb"

print("🌐 Loading DraftKings MLB page...")
driver.get(url)
time.sleep(6)

# Expand 'Game Props' or scroll if needed
print("🔍 Searching for NRFI/YRFI lines...")

games = []
rows = driver.find_elements(By.CLASS_NAME, "event-cell")

print(f"🔎 Found {len(rows)} potential prop blocks...\n")

for row in rows:
    try:
        teams = row.find_element(By.CLASS_NAME, "event-cell__name-text").text
        print("📋 Raw row:", row.text)

        lines = row.find_elements(By.CLASS_NAME, "sportsbook-outcome-cell__element")
        if len(lines) < 2:
            continue

        yes_text = lines[0].text
        no_text = lines[1].text

        if "Yes" in yes_text or "No" in no_text:
            away_team, home_team = teams.split(" @ ")
            yrfi_odds = lines[0].text.split("\n")[-1]
            nrfi_odds = lines[1].text.split("\n")[-1]

            games.append({
                "Game Date": datetime.now(timezone("US/Eastern")).strftime("%Y-%m-%d"),
                "Away Team": away_team.strip(),
                "Home Team": home_team.strip(),
                "YRFI Odds": yrfi_odds,
                "NRFI Odds": nrfi_odds
            })

    except Exception as e:
        print(f"⚠️ Error reading row: {e}")
        continue

driver.quit()

# === Format output
df = pd.DataFrame(games)

if df.empty:
    print("❌ No props scraped — check if props are live or inspect class names.")
    exit()

# Safely clean odds
df["YRFI Odds"] = df["YRFI Odds"].astype(str).str.replace("−", "-").str.replace("+", "").str.strip()
df["NRFI Odds"] = df["NRFI Odds"].astype(str).str.replace("−", "-").str.replace("+", "").str.strip()

# Convert to integers if possible
df["YRFI Odds"] = pd.to_numeric(df["YRFI Odds"], errors="coerce")
df["NRFI Odds"] = pd.to_numeric(df["NRFI Odds"], errors="coerce")

# Drop any rows with invalid odds
df = df.dropna(subset=["YRFI Odds", "NRFI Odds"]).astype({"YRFI Odds": int, "NRFI Odds": int})

print("\n✅ DraftKings YRFI odds scraped:")
print(df)

df.to_csv("data/yrfi_market_odds.csv", index=False)
print("\n💾 Saved to data/yrfi_market_odds.csv")
