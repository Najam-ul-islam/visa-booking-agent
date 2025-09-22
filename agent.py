# import os
# import smtplib
# import time
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from datetime import datetime
# from apscheduler.schedulers.background import BackgroundScheduler

# from openai import OpenAI
# from openai.agents import Agent, tool
# import google.generativeai as genai

# from booking_slots import extract_slots, save_slots_to_csv

# # ---------------- Config ----------------
# CHECK_INTERVAL_MINUTES = 30  # check every 30 minutes
# MAX_MONTHS_AHEAD = 5
# LAST_KNOWN_SLOTS = set()

# # Email settings
# EMAIL_SENDER = os.getenv("EMAIL_SENDER", "your_email@gmail.com")
# EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "your_app_password")  # Gmail app password
# EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER", "receiver_email@gmail.com")
# SMTP_SERVER = "smtp.gmail.com"
# SMTP_PORT = 587

# # ---------------- Gemini Setup ----------------
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# def gemini_reasoning(prompt: str):
#     try:
#         model = genai.GenerativeModel("gemini-2.5-flash")
#         resp = model.generate_content(prompt)
#         return resp.text
#     except Exception as e:
#         print(f"[⚠️ Gemini failed] {e}")
#         return None

# # ---------------- OpenAI Setup ----------------
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# def openai_reasoning(prompt: str, model="gpt-4.1"):
#     resp = client.chat.completions.create(
#         model=model,
#         messages=[
#             {"role": "system", "content": "You are a visa slot monitoring agent."},
#             {"role": "user", "content": prompt}
#         ]
#     )
#     return resp.choices[0].message.content

# # ---------------- Hybrid Reasoner ----------------
# def hybrid_reasoner(prompt: str) -> str:
#     result = gemini_reasoning(prompt)
#     if result:
#         return result
#     return openai_reasoning(prompt)

# # ---------------- Email Notification ----------------
# def send_email(subject: str, body: str):
#     """Send an email notification."""
#     try:
#         msg = MIMEMultipart()
#         msg["From"] = EMAIL_SENDER
#         msg["To"] = EMAIL_RECEIVER
#         msg["Subject"] = subject
#         msg.attach(MIMEText(body, "plain"))

#         server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
#         server.starttls()
#         server.login(EMAIL_SENDER, EMAIL_PASSWORD)
#         server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
#         server.quit()
#         print(f"[📧 Email sent] {subject}")
#     except Exception as e:
#         print(f"[❌ Email error] {e}")

# # ---------------- Tools ----------------
# @tool
# def check_slots(months: int = MAX_MONTHS_AHEAD) -> str:
#     """Check visa booking slots for the next N months."""
#     from selenium import webdriver
#     driver = webdriver.Chrome()
#     slots = extract_slots(driver, months_ahead=months)
#     save_slots_to_csv(slots)
#     driver.quit()

#     global LAST_KNOWN_SLOTS
#     new_slots = [
#         f"{s['month']} {s.get('day')} {s.get('weekday')} {s.get('time','')}"
#         for s in slots
#         if s.get("status") == "Available" and (s.get("weekday") or "").upper() not in {"FRI","SAT","SUN"}
#     ]

#     fresh = set(new_slots) - LAST_KNOWN_SLOTS
#     LAST_KNOWN_SLOTS.update(new_slots)

#     if fresh:
#         message = f"🚨 New visa slots found ({len(fresh)}):\n\n" + "\n".join(fresh)
#         notify_user(message)
#     else:
#         print(f"[{datetime.now()}] No new slots.")

#     return f"Found {len(slots)} total slots, {len(new_slots)} available."

# @tool
# def notify_user(message: str) -> str:
#     """Send email notification to the user."""
#     send_email("🚨 New Visa Slot Alert", message)
#     return "User notified by email."

# # ---------------- Agent ----------------
# agent = Agent(
#     name="VisaBookingAgent",
#     instructions="""
#     You are an agent that monitors visa appointment slots.
#     - Use `check_slots` regularly.
#     - If new weekday slots appear, call `notify_user`.
#     - Always reason with hybrid (Gemini first, OpenAI fallback).
#     """,
#     model="gpt-4.1",
#     tools=[check_slots, notify_user],
# )

# # ---------------- Autonomous Loop ----------------
# def scheduled_job():
#     query = f"Check visa slots for the next {MAX_MONTHS_AHEAD} months and notify me if available."
#     reasoning = hybrid_reasoner(query)
#     print(f"[🧠 Reasoning] {reasoning}")
#     session = agent.run(client)

# if __name__ == "__main__":
#     print("🚀 Starting Autonomous Visa Booking Agent...")

#     scheduler = BackgroundScheduler()
#     scheduler.add_job(scheduled_job, "interval", minutes=CHECK_INTERVAL_MINUTES)
#     scheduler.start()

#     try:
#         while True:
#             time.sleep(60)
#     except (KeyboardInterrupt, SystemExit):
#         scheduler.shutdown()
#         print("🛑 Agent stopped.")






# import time
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from main import run_scraper   # ✅ Import scraper logic
# from config.settings import EMAIL, EMAIL_APP_PASSWORD, SMTP_PORT, SMTP_SERVER, CHECK_INTERVAL, RECIPIENT_EMAIL
# import os


# # Email Config
# SMTP_SERVER = SMTP_SERVER if SMTP_SERVER is not None else "smtp.gmail.com"
# if SMTP_SERVER is None:
#     SMTP_SERVER = "smtp.gmail.com"
# SMTP_PORT = SMTP_PORT if SMTP_PORT is not None else 587
# if SMTP_PORT is None:
#     SMTP_PORT = 587
# EMAIL_SENDER = EMAIL
# EMAIL_PASSWORD = EMAIL_APP_PASSWORD   # Use App Password (not Gmail password!)
# EMAIL_RECIPIENT = RECIPIENT_EMAIL if RECIPIENT_EMAIL is not None else "default_receiver@example.com"

# # Ensure CHECK_INTERVAL is a number (seconds)
# try:
#     CHECK_INTERVAL = float(CHECK_INTERVAL)
# except (TypeError, ValueError):
#     CHECK_INTERVAL = 900  # Default to 15 minutes if not set or invalid


# def send_email_notification(slots):
#     """Send email notification when available slots are found."""
#     subject = "Visa Booking Slot Alert 🚨"
#     body = "The following slots are available:\n\n"
#     for s in slots:
#         body += f"{s.get('date', '?')} ({s.get('weekday','?')}) {s.get('time','?')} → {s.get('status','?')}\n"

#     msg = MIMEMultipart()
#     msg["From"] = EMAIL_SENDER
#     msg["To"] = EMAIL_RECIPIENT if EMAIL_RECIPIENT is not None else EMAIL_RECIPIENT
#     msg["Subject"] = subject
#     msg.attach(MIMEText(body, "plain"))

#     try:
#         server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
#         server.starttls()
#         if EMAIL_PASSWORD is None:
#             raise ValueError("EMAIL_PASSWORD is not set. Please provide a valid email app password.")
#         server.login(EMAIL_SENDER, EMAIL_PASSWORD)
#         server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, msg.as_string())
#         server.quit()
#         print(f"[📧] Email sent to {EMAIL_RECIPIENT}")
#     except Exception as e:
#         print(f"[❌] Failed to send email: {e}")


# def agent_loop():
#     """Continuously check for slots and notify via email."""
#     print("[🤖] Agent started. Checking slots every 15 minutes...")

#     while True:
#         slots = run_scraper(headless=True)   # ✅ Headless run for automation

#         # Filter available slots only (weekdays)
#         available = [
#             s for s in slots
#             if s.get("status") == "Available" and (s.get("weekday") or "").upper() not in {"FRI", "SAT", "SUN"}
#         ]

#         if available:
#             print(f"[🎉] Found {len(available)} available slots! Sending email...")
#             time.sleep(float(CHECK_INTERVAL))  # Wait before next check
#         else:
#             print("[ℹ️] No available slots found this run.")

#         time.sleep(CHECK_INTERVAL)  # Wait before next check


# if __name__ == "__main__":
#     agent_loop()



# import time
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from main import run_scraper  
# from config.settings import EMAIL, EMAIL_APP_PASSWORD,SMTP_SERVER, RECIPIENT_EMAIL


# # Email Config
# SMTP_SERVER = str(SMTP_SERVER)
# SMTP_PORT: int = 587
# EMAIL_SENDER = EMAIL
# EMAIL_PASSWORD = EMAIL_APP_PASSWORD   # Use App Password (not Gmail password!)
# EMAIL_RECIPIENT = RECIPIENT_EMAIL or "m.najamulislam88@gmail.com"

# CHECK_INTERVAL = 15*60

# # Ensure CHECK_INTERVAL is a number (seconds)
# try:
#     CHECK_INTERVAL = float(CHECK_INTERVAL)
# except (TypeError, ValueError):
#     CHECK_INTERVAL = 900  # Default to 15 minutes


# def send_email_notification(slots):
#     """Send email notification when available slots are found."""
#     subject = "Visa Booking Slot Alert 🚨"
#     body = "The following slots are available:\n\n"
#     for s in slots:
#         body += f"{s.get('date', '?')} ({s.get('weekday','?')}) {s.get('time','?')} → {s.get('status','?')}\n"

#     msg = MIMEMultipart()
#     msg["From"] = EMAIL_SENDER
#     msg["To"] = EMAIL_RECIPIENT
#     msg["Subject"] = subject
#     msg.attach(MIMEText(body, "plain"))

#     if not EMAIL_PASSWORD:
#         print("[❌] EMAIL_PASSWORD is missing. Cannot send email.")
#         return

#     try:
#         with smtplib.SMTP(str(SMTP_SERVER), SMTP_PORT) as server:
#             server.starttls()
#             server.login(EMAIL_SENDER, EMAIL_PASSWORD)
#             server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, msg.as_string())

#         print(f"[📧] Email sent to {EMAIL_RECIPIENT}")
#     except Exception as e:
#         print(f"[❌] Failed to send email: {e}")


# def agent_loop():
#     """Continuously check for slots and notify via email."""
#     print(f"[🤖] Agent started. Checking slots every {int(CHECK_INTERVAL/60)} minutes...")

#     while True:
#         slots = run_scraper(headless=True) or []

#         # Filter available slots only (weekdays)
#         available = [
#             s for s in slots
#             if s.get("status") == "Available" and (s.get("weekday") or "").upper() not in {"FRI", "SAT", "SUN"}
#         ]

#         if available:
#             print(f"[🎉] Found {len(available)} available slots! Sending email...")
#             send_email_notification(available)
#         else:
#             print("[ℹ️] No available slots found this run.")

#         time.sleep(CHECK_INTERVAL)  # Wait before next check


# if __name__ == "__main__":
#     agent_loop()





import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from main import run_scraper  
from config.settings import EMAIL, EMAIL_APP_PASSWORD, SMTP_SERVER, RECIPIENT_EMAIL


# Email Config
SMTP_SERVER: str  = SMTP_SERVER
SMTP_PORT: int = 587
EMAIL_SENDER = EMAIL
EMAIL_PASSWORD = EMAIL_APP_PASSWORD   # Use App Password (not Gmail password!)
EMAIL_RECIPIENT = RECIPIENT_EMAIL or "default_receiver@example.com"

CHECK_INTERVAL = 15 * 60  # 15 minutes


def send_email_notification(slots):
    """Send email notification when available slots are found."""
    subject = "Visa Booking Slot Alert 🚨"
    body = "The following slots are available:\n\n"
    for s in slots:
        body += f"{s.get('date','?')} ({s.get('weekday','?')}) {s.get('time','?')} → {s.get('status','?')}\n"

    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECIPIENT
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    if not EMAIL_PASSWORD:
        print("[❌] EMAIL_PASSWORD is missing. Cannot send email.")
        return

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, msg.as_string())
        print(f"[📧] Email sent to {EMAIL_RECIPIENT}")
    except Exception as e:
        print(f"[❌] Failed to send email: {e}")


def agent_loop():
    """Continuously check for slots and notify via email."""
    print(f"[🤖] Agent started. Checking slots every {int(CHECK_INTERVAL/60)} minutes...")

    while True:
        try:
            slots = run_scraper(headless=True) or []

            # Filter available slots only (weekdays)
            available = [
                s for s in slots
                if s.get("status") == "Available"
                and (s.get("weekday") or "").upper() not in {"FRI", "SAT", "SUN"}
            ]

            if available:
                print(f"[🎉] Found {len(available)} available slots! Sending email...")
                send_email_notification(available)
            else:
                print("[ℹ️] No available slots found this run.")

        except Exception as e:
            print(f"[❌] Agent loop crashed: {e}")

        time.sleep(CHECK_INTERVAL)  # Wait before next check


if __name__ == "__main__":
    agent_loop()
