# from booking.browser import init_browser
# from booking.login import login
# from booking.slots import save_slots_to_csv

# def main():
#     # Start browser (headless=False so you can see & solve Turnstile)
#     driver = init_browser(headless=False)

#     try:
#         # Run login flow
#         if login(driver):
#             # Extract slots after successful login
#             from booking.slots import extract_slots
#             slots = extract_slots(driver)

#             if slots:
#                 print(f"\n📅 All slots found: {len(slots)}")
#                 for s in slots:
#                     print("  ", s)

#                 # Save into CSV
#                 save_slots_to_csv(slots)
#             else:
#                 print("\n⚠️ No slots extracted this run.")
#         else:
#             print("\n❌ Login failed. No slots extracted.")

#     finally:
#         # Keep browser open after run (optional)
#         input("\nPress Enter to close browser...")
#         driver.quit()


# if __name__ == "__main__":
#     main()



# from booking.browser import init_browser
# from booking.login import login
# from booking.slots import extract_slots, save_slots_to_csv


# def run_scraper(headless: bool = True):
#     """
#     Run the slot scraper:
#     - Starts browser
#     - Logs in
#     - Extracts slots
#     - Saves to CSV
#     Returns the slots list (so agent.py can reuse it).
#     """
#     driver = init_browser(headless=headless)
#     slots = []

#     try:
#         # Run login flow
#         if login(driver):
#             slots = extract_slots(driver)

#             if slots:
#                 print(f"\n📅 All slots found: {len(slots)}")
#                 for s in slots:
#                     print("  ", s)

#                 # Save into CSV
#                 save_slots_to_csv(slots)
#             else:
#                 print("\n⚠️ No slots extracted this run.")
#         else:
#             print("\n❌ Login failed. No slots extracted.")

#     finally:
#         driver.quit()

#     return slots


# def main():
#     # Default run (headless=False so you can watch it for debugging)
#     run_scraper(headless=False)


# if __name__ == "__main__":
#     main()



# from booking.browser import init_browser
# from booking.login import login
# from booking.slots import extract_slots, save_slots_to_csv


# def run_scraper(headless: bool = True):
#     """
#     Run the visa booking scraper once and return extracted slots.
#     """
#     driver = init_browser(headless=headless)
#     slots = []

#     try:
#         if login(driver):
#             slots = extract_slots(driver)

#             if slots:
#                 print(f"\n📅 Extracted {len(slots)} slot(s).")
#                 save_slots_to_csv(slots)
#             else:
#                 print("\n⚠️ No slots extracted this run.")
#         else:
#             print("\n❌ Login failed. No slots extracted.")

#     finally:
#         driver.quit()

#     return slots


# def main():
#     """Manual run (interactive mode)."""
#     slots = run_scraper(headless=False)

#     if slots:
#         print("\n📅 All slots:")
#         for s in slots:
#             print("  ", s)
#     else:
#         print("\n⚠️ No slots extracted this run.")


# if __name__ == "__main__":
#     main()


import argparse
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from booking.browser import init_browser
from booking.login import login
from booking.slots import extract_slots, save_slots_to_csv
from config.settings import EMAIL, EMAIL_APP_PASSWORD, SMTP_SERVER, RECIPIENT_EMAIL


# ---------------- Email Setup ----------------
SMTP_SERVER = str(SMTP_SERVER or "smtp.gmail.com")
SMTP_PORT = 587
EMAIL_SENDER = EMAIL
EMAIL_PASSWORD = EMAIL_APP_PASSWORD
EMAIL_RECIPIENT = RECIPIENT_EMAIL or "default_receiver@example.com"

DEFAULT_INTERVAL = 15 * 60  # 15 minutes


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
        print("[❌] EMAIL_PASSWORD missing. Cannot send email.")
        return

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, msg.as_string())
        print(f"[📧] Email sent to {EMAIL_RECIPIENT}")
    except Exception as e:
        print(f"[❌] Failed to send email: {e}")


# ---------------- Scraper Logic ----------------
def run_scraper(headless=False):
    """Run one scraping session (login → extract → save → quit)."""
    driver = init_browser(headless=headless)
    slots = []
    try:
        if login(driver):
            slots = extract_slots(driver) or []
            if slots:
                save_slots_to_csv(slots)
        else:
            print("❌ Login failed. No slots extracted.")
    finally:
        driver.quit()
    return slots


# ---------------- Agent Loop ----------------
def agent_loop(interval: int):
    """Run autonomous agent mode (loops forever)."""
    print(f"[🤖] Agent started. Checking every {interval // 60} minutes...")

    while True:
        print("\n==============================")
        print("[*] Starting a new browser session...")
        slots = run_scraper(headless=False)  # visible browser each run

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

        print(f"[*] Sleeping {interval // 60} minutes before next run...")
        time.sleep(interval)


# ---------------- Main Entry ----------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visa Booking Slot Checker")
    parser.add_argument("--agent", action="store_true",
                        help="Run in autonomous agent mode (continuous monitoring)")
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL,
                        help="Check interval in seconds (default: 900 = 15 minutes)")
    args = parser.parse_args()

    if args.agent:
        agent_loop(args.interval)
    else:
        slots = run_scraper(headless=False)  # one-time scrape
        if slots:
            print(f"\n📅 All slots found: {len(slots)}")
            for s in slots:
                print("  ", s)
        else:
            print("\n⚠️ No slots extracted this run.")
