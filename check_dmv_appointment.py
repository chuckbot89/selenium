from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import time

# --- CONFIGURE YOUR EMAIL SETTINGS ---
EMAIL_SENDER = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password_here"
EMAIL_RECIPIENT = "destination_email@example.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# --- Headless Chrome Setup ---
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
    # Step 1: Click "Colorado Springs"
    location_buttons = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "DataControlBtn")))
    for btn in location_buttons:
        if "Colorado Springs" in btn.text:
            print("[DEBUG] Clicking 'Colorado Springs'")
            btn.click()
            break
    else:
        raise Exception("Could not find 'Colorado Springs'")

    time.sleep(2)

    # Step 2: Click the service option
    service_buttons = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "DataControlBtn")))
    for btn in service_buttons:
        if "Renew Colorado Driver License/ID/Permit" in btn.text:
            print("[DEBUG] Clicking 'Renew Colorado Driver License/ID/Permit'")
            btn.click()
            break
    else:
        raise Exception("Could not find desired service option.")

    time.sleep(3)

    # Step 3: Extract appointment time
    time_slot = wait.until(EC.presence_of_element_located((By.ID, "SingleDateTime")))
    raw_datetime = time_slot.get_attribute("data-datetime")
    print(f"[+] Found appointment slot: {raw_datetime}")

    try:
        parsed = datetime.strptime(raw_datetime, "%m/%d/%Y %I:%M:%S %p")
        formatted = parsed.strftime("%A, %B %d, %Y at %I:%M %p")
    except Exception:
        formatted = raw_datetime

    message_body = f"Earliest available appointment: {formatted}"
    send_email("Colorado Springs DMV Appointment Found", message_body)

except Exception as e:
    print("[-] ERROR:", e)
    send_email("DMV Appointment Script Error", f"An error occurred: {e}")

finally:
    print("[DEBUG] Closing browser.")
    driver.quit()
# --- END OF SCRIPT ---