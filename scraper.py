import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from firebase_config import db

# ---------- UNIVERSAL STATIC SCRAPER ----------
def static_scrape(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        data = []

        # Find all headlines and paragraphs
        elements = soup.find_all(["h1", "h2", "h3", "p", "li"])

        for el in elements:
            text = el.get_text(strip=True)
            # Only keep meaningful text (more than 30 characters)
            if len(text) > 30:
                data.append(text)

        # Remove duplicates
        data = list(dict.fromkeys(data))

        print(f"[Static Scraper] Found {len(data)} items")
        return data

    except Exception as e:
        print(f"[Static Error]: {e}")
        return []

# ---------- UNIVERSAL DYNAMIC SCRAPER ----------
def dynamic_scrape(url):
    driver = None
    try:
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        driver.get(url)
        time.sleep(5) # Wait for JS to load

        soup = BeautifulSoup(driver.page_source, "html.parser")
        data = []

        elements = soup.find_all(["h1", "h2", "h3", "p", "li"])

        for el in elements:
            text = el.get_text(strip=True)
            if len(text) > 30:
                data.append(text)

        data = list(dict.fromkeys(data))
        
        driver.quit()
        print(f"[Dynamic Scraper] Found {len(data)} items")
        return data

    except Exception as e:
        if driver:
            driver.quit()
        print(f"[Dynamic Error]: {e}")
        return []

# ---------- SAVE TO FIREBASE ----------
def save_to_firebase(url, data):
    if not data:
        print("No data to save.")
        return

    try:
        now = datetime.now()
        # Create a dictionary for organized storage
        payload = {
            "url": url,
            "data": data,
            "item_count": len(data),
            "timestamp": now,
            "readable_date": now.strftime("%d %B %Y, %I:%M %p")
        }

        db.collection("scraped_data").add(payload)
        print("[Firebase] Data successfully saved!")

    except Exception as e:
        print(f"[Firebase Error]: {e}")