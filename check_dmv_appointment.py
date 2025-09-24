from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import time
import os
from dotenv import load_dotenv
  
# --- Load Environment Variables ---  
load_dotenv()

# --- CONFIGURE YOUR EMAIL SETTINGS ---
EMAIL_SENDER = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# --- CONFIGURE YOUR DATE RANGE (inclusive) ---
DATE_RANGE_START = datetime.now()
DATE_RANGE_END = datetime(2025, 10, 10)

# --- SETUP WEBDRIVER ---
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

url = "https://coloradoappt.cxmflow.com/Appointment/Index/d74f48b1-33a9-428c-acd1-d7d1bfc9555c"
driver.get(url)
print("[DEBUG] Page loaded.")

wait = WebDriverWait(driver, 15)

def send_email(subject, body):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECIPIENT

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, msg.as_string())
        print("[DEBUG] Email sent successfully.")
    except Exception as e:
        print(f"[-] Failed to send email: {e}")

try:
    # Step 1: Select "Colorado Springs"
    location_buttons = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "DataControlBtn")))
    for btn in location_buttons:
        if "Colorado Springs" in btn.text:
            print("[DEBUG] Clicking 'Colorado Springs'")
            btn.click()
            break
    else:
        raise Exception("Could not find 'Colorado Springs'")

    time.sleep(2)

    # Step 2: Select the service
    service_buttons = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "DataControlBtn")))
    for btn in service_buttons:
        if "Renew Colorado Driver License/ID/Permit" in btn.text:
            print("[DEBUG] Clicking service option")
            btn.click()
            break
    else:
        raise Exception("Service option not found.")

    time.sleep(5)

    # Step 3: Get the appointment datetime
    time_slot = wait.until(EC.presence_of_element_located((By.ID, "SingleDateTime")))
    raw_datetime = time_slot.get_attribute("data-datetime")
    print(f"[DEBUG] Raw appointment string: {raw_datetime}")

    # Parse to datetime object
    try:
        parsed = datetime.strptime(raw_datetime, "%m/%d/%Y %I:%M:%S %p")
        print(f"[DEBUG] Parsed appointment datetime: {parsed}")
    except ValueError:
        raise Exception(f"Could not parse datetime from: {raw_datetime}")

    # Step 4: Check if appointment is within range
    if DATE_RANGE_START <= parsed <= DATE_RANGE_END:
        formatted = parsed.strftime("%A, %B %d, %Y at %I:%M %p")
        subject = "DMV Appointment Available Within Your Date Range"
        body = f"Good news! An appointment is available:\n\n{formatted}"
        send_email(subject, body)
    else:
        print(f"[INFO] Appointment found, but outside of range: {parsed.strftime('%Y-%m-%d')}")

except Exception as e:
    print("[-] ERROR:", e)
    send_email("DMV Script Error", f"An error occurred:\n\n{e}")

finally:
    print("[DEBUG] Closing browser.")
    driver.quit()
