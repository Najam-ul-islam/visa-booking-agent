# import csv
# import json
# import os
# import time
# import random
# import re
# from datetime import datetime, timezone
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException
# from bs4 import BeautifulSoup
# import calendar
# from dateutil import parser
# from tabulate import tabulate
# from collections import defaultdict

# from config.settings import EMAIL, PASSWORD, SAVE_SCREENSHOTS

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from config.settings import EMAIL, PASSWORD
from .utils import _human_sleep, _save_screenshot, solve_math_challenge


def login(driver, username: str = EMAIL, password: str = PASSWORD, headless=False) -> bool:
    """Only login flow. Returns True if login succeeded, False otherwise."""
    root = "https://schedule.cf-grcon-isl-pakistan.com/"
    print(f"[*] Opening homepage: {root}")
    driver.get(root)
    _save_screenshot(driver, "step1_home")

    # ---- Handle Turnstile ----
    print("[*] Waiting for Turnstile or redirect...")
    try:
        WebDriverWait(driver, 20).until(
            lambda d: "/landing/home" in d.current_url or len(d.find_elements(By.TAG_NAME, "iframe")) > 0
        )
    except Exception:
        pass
    _save_screenshot(driver, "step2_turnstile")

    if "/landing/home" not in driver.current_url:
        print("[!] Could not auto-pass Turnstile. Solve manually if visible.")
        if headless:
            raise RuntimeError("Headless=True but manual Turnstile solve required. Use headless=False.")
        else:
            print("[*] Waiting up to 2 minutes for manual Turnstile solve...")
            WebDriverWait(driver, 120).until(
                lambda d: "/landing/home" in d.current_url or "National visa for WORK" in d.page_source
            )
            print("[+] Turnstile solved manually → category page loaded ✅")
    _save_screenshot(driver, "step3_category")

    # ---- Category Page ----
    work_link = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.LINK_TEXT, "National visa for WORK"))
    )
    try:
        work_link.click()
        print("[+] Clicked 'National visa for WORK' link")
    except Exception:
        print("[!] Normal click failed, trying ActionChains...")
        actions = ActionChains(driver)
        actions.move_to_element(work_link).pause(0.5).click().perform()
    _human_sleep(2, 3)
    _save_screenshot(driver, "step4_after_work_click")

    # ---- Login Form ----
    email_box = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "name")))
    password_box = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "password")))
    print("[+] Found login form fields")

    email_box.clear(); email_box.send_keys(username); _human_sleep()
    password_box.clear(); password_box.send_keys(password); _human_sleep()
    _save_screenshot(driver, "step5_filled_login")

    try:
        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_btn.click()
        print("[+] Clicked submit button")
    except Exception:
        password_box.send_keys("\n")

    time.sleep(3)
    _save_screenshot(driver, "step6_after_submit")

    # ---- Solve Math Challenge ----
    solve_math_challenge(driver)

    # ---- Post-login validation ----
    try:
        WebDriverWait(driver, 15).until(
            lambda d: "Log out" in d.page_source or "Available" in d.page_source
        )
        print("[✅] Logged in successfully!")
        _save_screenshot(driver, "step8_logged_in")
        return True
    except TimeoutException:
        print("[❌] Login failed or slots page not found.")
        _save_screenshot(driver, "step8_login_failed")
        return False
# ===================================================================================

# def _human_sleep(min_s=0.4, max_s=1.2):
#     """Random short sleep to mimic human typing delays."""
#     time.sleep(random.uniform(min_s, max_s))


# def _save_screenshot(driver, step_name: str):
#     """Save screenshot + HTML dump into ./screenshots with timestamped filenames."""
#     if not SAVE_SCREENSHOTS:
#         return

#     os.makedirs("screenshots", exist_ok=True)
#     timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

#     # Screenshot
#     png_filename = f"{timestamp}_{step_name}.png"
#     png_path = os.path.join("screenshots", png_filename)
#     driver.save_screenshot(png_path)
#     print(f"[📸] Saved screenshot: {png_path}")

#     # HTML dump
#     html_filename = f"{timestamp}_{step_name}.html"
#     html_path = os.path.join("screenshots", html_filename)
#     with open(html_path, "w", encoding="utf-8") as f:
#         f.write(driver.page_source)
#     print(f"[📄] Saved HTML dump: {html_path}")


# def solve_math_challenge(driver):
#     """Detect and solve simple math challenge if it appears."""
#     try:
#         challenge_box = WebDriverWait(driver, 5).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, "form input[type='text']"))
#         )
#         question_text = driver.find_element(By.CSS_SELECTOR, "form").text.strip()
#         print(f"[*] Math challenge detected: {question_text}")

#         # Try to capture with operator
#         match = re.search(r"(\d+)\s*([+\-*/])\s*(\d+)", question_text)

#         if match:
#             a, op, b = int(match.group(1)), match.group(2), int(match.group(3))
#         else:
#             # Fallback: just numbers, e.g. "1 1 =" or "5 3 ="
#             nums = re.findall(r"\d+", question_text)
#             if len(nums) == 2:
#                 a, b = int(nums[0]), int(nums[1])
#                 if a == b:
#                     op = "+"   # assume addition when numbers are equal
#                     print(f"[!] No operator found, assuming addition: {a} + {b}")
#                 else:
#                     op = "-"   # assume subtraction otherwise
#                     print(f"[!] No operator found, assuming subtraction: {a} - {b}")
#             else:
#                 raise RuntimeError("❌ Could not parse math question.")

#         # Solve equation
#         if op == "+": answer = a + b
#         elif op == "-": answer = a - b
#         elif op == "*": answer = a * b
#         elif op == "/": answer = a // b if b != 0 else 0
#         else: raise RuntimeError(f"Unknown operator {op}")

#         challenge_box.clear()
#         challenge_box.send_keys(str(answer))
#         challenge_box.submit()
#         print(f"[+] Solved math challenge: {a} {op} {b} = {answer}")

#         _save_screenshot(driver, "step_7_after_math_challenge")
#         time.sleep(3)
#         return True

#     except TimeoutException:
#         print("[*] No math challenge detected.")
#         return False


# # -------------Extract Slots and Save them into CSV-----------
# # Toggle here: use UTC or local timezone
# USE_UTC = True  

# def format_timestamp(ts: float) -> str:
#     """
#     Convert a POSIX timestamp to a formatted datetime string.
#     If USE_UTC=True → timezone-aware UTC datetime.
#     Else → system local timezone datetime.
#     """
#     if USE_UTC:
#         dt = datetime.fromtimestamp(ts, tz=timezone.utc)
#         return dt.strftime("%Y-%m-%d %H:%M UTC")
#     else:
#         dt = datetime.fromtimestamp(ts)  # local time
#         return dt.strftime("%Y-%m-%d %H:%M %Z")

# # --------- Parse Slots data ----------
# def parse_slot_text(text: str) -> dict:
#     """
#     Parse a slot string into structured fields:
#     Month, Day, Date, Time, Status.
#     """
#     try:
#         # Try to parse any recognizable datetime
#         dt = parser.parse(text, fuzzy=True, dayfirst=True)

#         return {
#             "month": dt.strftime("%B"),     # March
#             "day": dt.strftime("%A"),       # Monday
#             "date": dt.strftime("%d"),      # 12
#             "time": dt.strftime("%I:%M %p"),# 10:30 AM
#             "status": "Available" if "available" in text.lower() else "Full" if "full" in text.lower() else "Unknown",
#             "raw": text.strip()
#         }
#     except Exception:
#         # Fallback if parsing fails
#         return {
#             "month": "",
#             "day": "",
#             "date": "",
#             "time": "",
#             "status": "Unknown",
#             "raw": text.strip()
#         }

# #  --------- Save slots to CSV ------------------
# def save_slots_to_csv(slots, folder="slot_data"):
#     """
#     Save extracted slots into daily CSV files with timezone-aware timestamps.
#     Each day gets its own CSV: slots_YYYY-MM-DD.csv
#     """
#     os.makedirs(folder, exist_ok=True)

#     # Current UTC/local date string
#     today = datetime.now(timezone.utc).strftime("%Y-%m-%d") if USE_UTC \
#         else datetime.now().strftime("%Y-%m-%d")

#     filename = os.path.join(folder, f"slots_{today}.csv")
#     file_exists = os.path.isfile(filename)

#     with open(filename, "a", newline="", encoding="utf-8") as f:
#         writer = csv.writer(f)

#         # Write header if file doesn't exist yet
#         if not file_exists:
#             writer.writerow(["Extracted_At", "Month", "Day", "Date", "Time", "Status"])

#         now_str = format_timestamp(datetime.now(timezone.utc).timestamp())

#         for slot in slots:
#             writer.writerow([
#                 now_str,
#                 slot.get("month"),
#                 slot.get("day"),
#                 slot.get("date"),
#                 slot.get("time"),
#                 slot.get("status")
#             ])

#     print(f"[💾] Saved {len(slots)} slots into {filename}")

# # --------- Extract Slots ----------------
# def extract_slots(driver):
#     """
#     Extract slots from booking calendar.
#     Phase 1: Print all months with their slots (available & not available).
#     Phase 2: Print available slots only.
#     """
#     print("[*] Looking for booking calendar...")

#     slots = []
#     _save_screenshot(driver, "step9_slots_page")

#     soup = BeautifulSoup(driver.page_source, "html.parser")
#     slot_elements = soup.select(".ss_slot, .slot, table.ss_calendar td")

#     for elem in slot_elements:
#         text = elem.get_text(strip=True)
#         if not text:
#             continue

#         # Skip junk banners / notices
#         if any(skip in text.lower() for skip in [
#             "signed in", "notice", "successfully logged in",
#             "help", "settings", "sign out"
#         ]):
#             continue

#         slot = {
#             "month": "",
#             "day": "",
#             "date": "",
#             "time": "",
#             "status": "Not available",
#             "raw": text
#         }

#         # Status
#         if "available" in text.lower():
#             slot["status"] = "Available"
#         elif "full" in text.lower() or "no slots" in text.lower():
#             slot["status"] = "Full"

#         # Parse date (e.g. "Monday 13 October")
#         date_match = re.search(r"([A-Za-z]+)\s+(\d{1,2})\s+([A-Za-z]+)", text)
#         time_match = re.search(r"(\d{1,2}:\d{2}\s*(?:AM|PM)?)", text)

#         if date_match:
#             slot["day"] = date_match.group(1)
#             slot["date"] = date_match.group(2)
#             slot["month"] = date_match.group(3)

#         if time_match:
#             slot["time"] = time_match.group(1)

#         slots.append(slot)

#     # --------------------------
#     # Phase 1: Print all months
#     # --------------------------
#     grouped = defaultdict(list)
#     for s in slots:
#         grouped[s["month"] or "Unknown"].append(s)

#     print("\n📅 All slots (month-wise):")
#     for month, items in grouped.items():
#         print(f"\n--- {month} ---")
#         for s in items:
#             print(f"  {s['day']} {s['date']} {s['time']} → {s['status']}")

#     # --------------------------
#     # Phase 2: Print available slots only
#     # --------------------------
#     available = [s for s in slots if s["status"] == "Available"]

#     print("\n🎉 Available slots:")
#     if available:
#         for s in available:
#             print(f"  {s['day']} {s['date']} {s['month']} {s['time']} → {s['status']}")
#     else:
#         print("  ❌ No available slots right now.")

#     return slots



# # ------- Login Function --------

# def login(driver, username: str = EMAIL, password: str = PASSWORD, headless=False):
#     """Single login attempt flow with slot extraction."""
#     root = "https://schedule.cf-grcon-isl-pakistan.com/"
#     print(f"[*] Opening homepage: {root}")
#     driver.get(root)
#     _save_screenshot(driver, "step1_home")

#     # ---- Handle Turnstile ----
#     print("[*] Waiting for Turnstile or redirect...")
#     try:
#         WebDriverWait(driver, 20).until(
#             lambda d: "/landing/home" in d.current_url or len(d.find_elements(By.TAG_NAME, "iframe")) > 0
#         )
#     except Exception:
#         pass
#     _save_screenshot(driver, "step2_turnstile")

#     if "/landing/home" not in driver.current_url:
#         print("[!] Could not auto-pass Turnstile. Solve manually if visible.")
#         if headless:
#             raise RuntimeError("Headless=True but manual Turnstile solve required. Use headless=False.")
#         else:
#             print("[*] Waiting up to 2 minutes for manual Turnstile solve...")
#             WebDriverWait(driver, 120).until(
#                 lambda d: "/landing/home" in d.current_url or "National visa for WORK" in d.page_source
#             )
#             print("[+] Turnstile solved manually → category page loaded ✅")
#     _save_screenshot(driver, "step3_category")

#     # ---- Category Page ----
#     work_link = WebDriverWait(driver, 30).until(
#         EC.presence_of_element_located((By.LINK_TEXT, "National visa for WORK"))
#     )
#     try:
#         work_link.click()
#         print("[+] Clicked 'National visa for WORK' link")
#     except Exception:
#         print("[!] Normal click failed, trying ActionChains...")
#         actions = ActionChains(driver)
#         actions.move_to_element(work_link).pause(0.5).click().perform()
#     _human_sleep(2, 3)
#     _save_screenshot(driver, "step4_after_work_click")

#     # ---- Login Form ----
#     email_box = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "name")))
#     password_box = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "password")))
#     print("[+] Found login form fields")

#     email_box.clear()
#     email_box.send_keys(username)
#     _human_sleep()
#     password_box.clear()
#     password_box.send_keys(password)
#     _human_sleep()
#     _save_screenshot(driver, "step5_filled_login")

#     try:
#         submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
#         submit_btn.click()
#         print("[+] Clicked submit button")
#     except Exception:
#         password_box.send_keys("\n")

#     time.sleep(3)
#     _save_screenshot(driver, "step6_after_submit")

#     # ---- Solve Math Challenge if needed ----
#     solve_math_challenge(driver)

#     # ---- Post-login validation ----
#     try:
#         WebDriverWait(driver, 15).until(
#             lambda d: "Log out" in d.page_source or "Available" in d.page_source
#         )
#         print("[✅] Logged in successfully, slots page available.")
#         _save_screenshot(driver, "step8_logged_in")

#         # Extract slots
#         slots = extract_slots(driver)
#         if slots:
#             available = [s for s in slots if s["status"] == "Available"]
#             if available:
#                 print(f"[🎉] Found {len(available)} available slots!")
#             else:
#                 print("[ℹ️] No available slots right now.")
#         return True

#     except TimeoutException:
#         print("[❌] Login failed or slots page not found.")
#         _save_screenshot(driver, "step8_login_failed")
#         return False

