import requests
from bs4 import BeautifulSoup
import json
import logging
import smtplib
from email.message import EmailMessage
from difflib import get_close_matches
from datetime import datetime

# --- CONFIGURATION ---
TRACKER_FILE = 'stanzas.json'
LOG_FILE = 'stanza_checker.log'
OCLC_URL = 'https://help.oclc.org/Library_Management/EZproxy/EZproxy_database_stanzas/Database_stanzas/EZproxy_database_stanzas_most_recent'
SMTP_SERVER = "smtp.gmail.com" # Update for your provider
SMTP_PORT_TLS = 587
EMAIL_USER = "your email"
EMAIL_PASS = "your app password" # Use an App Password, not your real password
RECIPIENT_EMAIL = "your email"

# Setup Logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_web_stanzas():
    try:
        response = requests.get(OCLC_URL, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        web_data = {}
        for table in soup.find_all('table'):
            for row in table.find_all('tr')[1:]:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    name = cols[0].get_text(strip=True)
                    date = cols[1].get_text(strip=True)
                    web_data[name] = date
        return web_data
    except Exception as e:
        logging.error(f"Scraping failed: {e}")
        return {}

def run_check():
    logging.info("Starting weekly check.")
    try:
        with open(TRACKER_FILE, 'r') as f:
            local_stanzas = json.load(f)
    except FileNotFoundError:
        logging.critical("Tracker file not found!")
        return

    web_stanzas = get_web_stanzas()
    if not web_stanzas:
        return

    updates_found = []
    local_keys = list(local_stanzas.keys())

    for web_name, web_date in web_stanzas.items():
        matches = get_close_matches(web_name.lower(), [k.lower() for k in local_keys], n=1, cutoff=0.8)
        if matches:
            local_key = next(k for k in local_keys if k.lower() == matches[0])
            if web_date > local_stanzas[local_key]:
                info = f"{local_key} (Web: {web_date}, Local: {local_stanzas[local_key]})"
                updates_found.append(info)
                logging.info(f"Update detected: {info}")
                local_stanzas[local_key] = web_date

    if updates_found:
        send_email(updates_found)
        with open(TRACKER_FILE, 'w') as f:
            json.dump(local_stanzas, f, indent=4)
    else:
        logging.info("No updates found.")

def send_email(updates):
    msg = EmailMessage()
    msg.set_content("The following EZproxy stanzas have been updated:\n\n" + "\n".join(updates))
    msg['Subject'] = f"EZproxy Update Alert - {datetime.now().strftime('%Y-%m-%d')}"
    msg['From'] = EMAIL_USER
    msg['To'] = RECIPIENT_EMAIL
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT_TLS, timeout=15) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        logging.info("Email notification sent successfully.")
    except Exception as e:
        logging.error(f"Email failed: {e}")

if __name__ == "__main__":
    run_check()
