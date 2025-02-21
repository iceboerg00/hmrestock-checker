import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests  # Telegram API

# Telegram-Konfiguration
TELEGRAM_BOT_TOKEN = "7890069335:AAEnE02uww7G9yFjCo6KJcgr-8SfRcqTp_k"  # Dein Telegram Bot Token
TELEGRAM_CHAT_IDS = ["5189098255", "8172032949"]  # Liste mit Telegram-Chat-IDs

# URL der Produktseite
PRODUCT_URL = "https://www2.hm.com/de_de/productpage.1268595001.html"
SIZE_TO_CHECK = "L"  # Größe, die überprüft werden soll

# Selenium WebDriver initialisieren
options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
options.add_argument("--headless")  # Browser läuft unsichtbar

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Funktion zum Überprüfen der Produktverfügbarkeit
def check_product_availability():
    driver.get(PRODUCT_URL)
    time.sleep(8)  # Warte länger auf das Laden der Seite
    
    try:
        size_labels = driver.find_elements(By.TAG_NAME, "label")
        if not size_labels:
            print("Keine Größenoptionen gefunden! Möglicherweise blockiert H&M den Zugriff.")
            print("Seiten-Quellcode:")
            print(driver.page_source[:1000])  # Ausgabe der ersten 1000 Zeichen der Seite
            return
        
        print("Gefundene Größenoptionen:")
        size_found = False
        
        for label in size_labels:
            size_name = label.get_attribute("for")  # Größe aus dem 'for'-Attribut holen
            if not size_name or any(x in size_name for x in ["ot-group-id", "chkbox-id", "select-all"]):
                continue  # Irrelevante Labels überspringen
            
            status_span = label.find_elements(By.TAG_NAME, "span")
            status = status_span[0].text.strip().lower() if status_span else "verfügbar"
            
            print(f"- {size_name}: (Status: {status})")  # Debug-Ausgabe aller Labels
            
            if SIZE_TO_CHECK == size_name:
                size_found = True
                if "ausverkauft" in status:
                    print(f"Größe {SIZE_TO_CHECK} ist ausverkauft. Keine Benachrichtigung gesendet.")
                elif "geringer bestand" in status or "verfügbar" in status:
                    print(f"Größe {SIZE_TO_CHECK} ist verfügbar! (Status: {status}) Nachricht wird gesendet.")
                    send_telegram_notification()
                    return
        
        if not size_found:
            print(f"Größe {SIZE_TO_CHECK} wurde auf der Seite nicht gefunden.")
    except Exception as e:
        print(f"Fehler bei der Größenprüfung: {e}")

# Funktion zum Versenden einer Telegram-Benachrichtigung
def send_telegram_notification():
    message = f"🔔 Das Produkt in Größe {SIZE_TO_CHECK} ist wieder auf Lager! Jetzt bestellen: {PRODUCT_URL}"
    
    for chat_id in TELEGRAM_CHAT_IDS:
        api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                print(f"✅ Telegram-Nachricht an {chat_id} gesendet!")
            else:
                print(f"⚠ Fehler beim Senden der Telegram-Nachricht an {chat_id}! HTTP-Code: {response.status_code}")
                print("Antwort von Telegram:", response.text)
        except Exception as e:
            print(f"❌ Schwerwiegender Fehler beim Senden der Telegram-Nachricht an {chat_id}: {e}")

check_product_availability()
