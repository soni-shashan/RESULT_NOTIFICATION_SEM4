from playwright.sync_api import sync_playwright
import time
from datetime import datetime
import smtplib
from email.message import EmailMessage
import logging
import sys
import os
from dotenv import load_dotenv
from flask import Flask
import threading
load_dotenv() 

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running."

def run_dummy_server():
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)

# Configure logging to output to stdout
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log(msg):
    logging.info(msg)

# ==== Email function ====
def send_email(subject, body, to_email):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = "lumbhanishashan1510@gmail.com"
    msg['To'] = to_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login("lumbhanishashan1510@gmail.com", os.environ.get("EMAIL_PASSWORD"))
            smtp.send_message(msg)
        log("📧 Email sent successfully.")
    except Exception as e:
        log("❌ Failed to send email:", e)

# ==== Exam checking function ====
def check_exam_schedule():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        page = browser.new_page()

        try:
            page.goto("https://charusat.edu.in:912/Uniexamresult/frmUniversityResult.aspx", timeout=60000)

            # Step-by-step selections
            page.select_option('select[name="ddlInst"]', '1')    # CSPIT
            page.wait_for_timeout(10000)

            page.select_option('select[name="ddlDegree"]', '155')  # BTECH(CS)
            page.wait_for_timeout(10000)

            page.select_option('select[name="ddlSem"]', '4')     # Semester 4
            page.wait_for_timeout(1500)

             # Extract available exams
            options = page.query_selector_all('#ddlScheduleExam option')
            for opt in options:
                text = opt.inner_text().strip()
                value = opt.get_attribute('value')
                if "2025" in text:
                    log(f'✅ 2025 Exam Found: {text}')

                    # Select 2025 Exam
                    page.select_option("#ddlScheduleExam", value)
                    page.wait_for_timeout(1500)

                    # Enter enrollment number
                    page.fill("#txtEnrNo", "23cs042")
                    page.click("#btnSearch")
                    log("🔍 Searching for SGPA...")

                    # Wait for SGPA element
                    page.wait_for_selector("#uclGrd1_lblSGPA", timeout=20000)
                    sgpa_element = page.query_selector("#uclGrd1_lblSGPA")
                    sgpa = sgpa_element.inner_text().strip()

                    log(f"🎓 SGPA found: {sgpa}")

                    # Send SGPA via email
                    send_email(
                        subject="🎓 SGPA Result for 23cs042 (2025 Exam)",
                        body=f"Exam: {text}\nEnrollment: 23cs042\nSGPA: {sgpa}\nChecked at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                        to_email="23cs042@charusat.edu.in"
                    )

                    return True  # Done

            log("🔄 2025 exam not found yet.")
            return False

        except Exception as e:
            log(f"❌ Error occurred: {str(e)}")
            return False

        finally:
            browser.close()

# ==== Run check every 1 hours ====
if __name__ == "__main__":
    threading.Thread(target=run_dummy_server).start()
    
    try:
        while True:
            found = check_exam_schedule()
            if found:
                break
            log('restart...')
            time.sleep(3600)
    except Exception as e:
        log(f"❌ Uncaught error: {e}")
        time.sleep(60)  # Retry after 1 minutes

