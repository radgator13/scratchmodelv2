import time
import pandas as pd
from datetime import datetime
from pytz import timezone
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# === Setup Chrome Headless ===
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options)

url = "https://sports.nj.betmgm.com/en/sports/baseball-7/betting/usa-9/mlb-6007"
print("🌐 Loading BetMGM MLB page...")
driver.get(url)
time.sleep(8)

# === Scroll and collect game tiles
print("🔄 Scrolling to reveal all games...")
for _ in range(15):
    driver.execute_script("window.scrollBy(0, 1500);")
    time.sleep(0.5)

print("🔍 Looking for clickable game tiles...")
game_tiles = driver.find_elements(By.XPATH, "//a[contains(@href, '/baseball/mlb/') and contains(@href, '/event/')]")

game_links = list(set([tile.get_attribute("href") for tile in game_tiles if tile.get_attribute("href")]))

print(f"🧭 Found {len(game_links)} games to visit.")

games = []

# === Step through each game page
for i, link in enumerate(game_links):
    try:
        print(f"\n📂 Opening ({i+1}/{len(game_links)}): {link}")
        driver.get(link)
        time.sleep(6)

        # Grab team names
        teams = driver.find_element(By.CLASS_NAME, "participants__names").text
        away_team, home_team = teams.split(" @ ")

        # Look for 1st Inning Run Prop
        try:
            prop_header = WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Will there be a run in the 1st Inning')]"))
            )
        except:
            print("⚠️ No YRFI prop on this game.")
            continue

        # Extract odds
        odds_container = prop_header.find_element(By.XPATH, "../../..")
        odds = odds_container.find_elements(By.CLASS_NAME, "option-price")

        if len(odds) < 2:
            print("⚠️ YRFI odds missing.")
            continue

        yrfi_odds = odds[0].text.replace("−", "-").replace("+", "").strip()
        nrfi_odds = odds[1].text.replace("−", "-").replace("+", "").strip()

        games.append({
            "Game Date": datetime.now(timezone("US/Eastern")).strftime("%Y-%m-%d"),
            "Away Team": away_team.strip(),
            "Home Team": home_team.strip(),
            "YRFI Odds": int(yrfi_odds),
            "NRFI Odds": int(nrfi_odds)
        })

    except Exception as e:
        print(f"❌ Error processing {link}: {e}")
        continue

driver.quit()

# === Save
df = pd.DataFrame(games)
if df.empty:
    print("❌ No YRFI props found. Try again later.")
else:
    print("\n✅ YRFI props scraped:")
    print(df)
    df.to_csv("data/yrfi_market_odds.csv", index=False)
    print("\n💾 Saved to data/yrfi_market_odds.csv")
