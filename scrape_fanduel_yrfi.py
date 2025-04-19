import time
import pandas as pd
from datetime import datetime
from pytz import timezone
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# === Setup undetected Chrome
options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--window-size=1920,1080")

driver = uc.Chrome(options=options)

main_url = "https://sportsbook.fanduel.com/navigation/mlb"
print("🌐 Loading FanDuel MLB page...")
driver.get(main_url)
time.sleep(6)

# === Scroll to load links
print("🔄 Scrolling...")
for _ in range(12):
    driver.execute_script("window.scrollBy(0, 1500);")
    time.sleep(0.5)

# === Step 1: Grab <a> tags with valid game links
print("🔍 Searching for game hrefs...")
hrefs = driver.find_elements(By.TAG_NAME, "a")
game_links = []

for el in hrefs:
    try:
        href = el.get_attribute("href")
        if href and "/baseball/mlb/" in href and "/event/" in href:
            game_links.append(href.split("?")[0])
    except:
        continue

# Remove duplicates
game_links = list(set(game_links))
print(f"🧭 Found {len(game_links)} unique game links.")

games = []

# === Step 2: Open each game and grab props
for i, url in enumerate(game_links):
    try:
        print(f"\n📂 Opening ({i+1}/{len(game_links)}): {url}")
        driver.get(url)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "event-title"))
        )
        time.sleep(3)

        matchup = driver.find_element(By.CLASS_NAME, "event-title").text
        away_team, home_team = matchup.split(" @ ")

        # Look for 1st Inning Over/Under market
        prop_block = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(text(), '1st Inning Over/Under 0.5 Runs')]")
            )
        )

        container = prop_block.find_element(By.XPATH, "..").find_element(By.XPATH, "..")
        odds = container.find_elements(By.CLASS_NAME, "outcome-price")

        if len(odds) < 2:
            print("⚠️ Found label but odds were missing.")
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
        print(f"❌ Failed to parse: {e}")
        continue

driver.quit()

# === Save the results
df = pd.DataFrame(games)
if df.empty:
    print("❌ No props scraped. Try again later.")
else:
    print("\n✅ YRFI props scraped:")
    print(df)
    df.to_csv("data/yrfi_market_odds.csv", index=False)
    print("\n💾 Saved to data/yrfi_market_odds.csv")
