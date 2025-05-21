import time
import re
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# —————— Konfiguration ——————
TELEGRAM_BOT_TOKEN = "7890069335:AAEnE02uww7G9yFjCo6KJcgr-8SfRcqTp_k"
TELEGRAM_CHAT_IDS = ["5189098255", "8172032949"]
PRODUCT_URL = (
    "https://www.popmart.com/de/products/1991/"
    "THE-MONSTERS-Big-into-Energy-Series-Vinyl-Plush-Pendant-Blind-Box"
)
# —————————————————————————

# Selenium WebDriver initialisieren
options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-gpu")
options.add_argument("--disable-software-rasterizer")
options.add_argument("--headless")
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=options
)

def send_telegram_notification():
    message = f"🔔 Dein Pop Mart-Blind-Box ist jetzt verfügbar! 👉 {PRODUCT_URL}"
    for chat_id in TELEGRAM_CHAT_IDS:
        api_url = (
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            f"?chat_id={chat_id}&text={message}"
        )
        try:
            resp = requests.get(api_url)
            print(f"{'✅' if resp.status_code==200 else '⚠️'} Telegram {chat_id}: {resp.status_code}")
        except Exception as e:
            print(f"❌ Telegram-Fehler {chat_id}: {e}")

def check_product_availability():
    driver.get(PRODUCT_URL)
    time.sleep(8)  # Warte auf dynamisches Laden
    
    html = driver.page_source.upper()
    has_add = bool(re.search(r"ADD TO CART", html))
    has_notify = bool(re.search(r"NOTIFY ME WHEN AVAILABLE", html))
    
    if has_add:
        print("🎉 „ADD TO CART“ im HTML gefunden → verfügbar!")
        send_telegram_notification()
    elif has_notify:
        print("🚫 „NOTIFY ME WHEN AVAILABLE“ im HTML gefunden → ausverkauft.")
    else:
        print("❓ Keine der gesuchten Phrasen gefunden. HTML prüfen:")
        # Debug: gib die ersten 500 Zeichen aus, damit du siehst, was drinsteht
        print(html[:500])

if __name__ == "__main__":
    check_product_availability()
    driver.quit()
