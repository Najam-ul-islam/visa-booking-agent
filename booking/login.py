import csv
import json
import os
import time
import random
import re
from datetime import datetime, timezone
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import calendar
from dateutil import parser
from tabulate import tabulate
from collections import defaultdict

from config.settings import EMAIL, PASSWORD, SAVE_SCREENSHOTS


def _human_sleep(min_s=0.4, max_s=1.2):
    """Random short sleep to mimic human typing delays."""
    time.sleep(random.uniform(min_s, max_s))


def _save_screenshot(driver, step_name: str):
    """Save screenshot + HTML dump into ./screenshots with timestamped filenames."""
    if not SAVE_SCREENSHOTS:
        return

    os.makedirs("screenshots", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Screenshot
    png_filename = f"{timestamp}_{step_name}.png"
    png_path = os.path.join("screenshots", png_filename)
    driver.save_screenshot(png_path)
    print(f"[📸] Saved screenshot: {png_path}")

    # HTML dump
    html_filename = f"{timestamp}_{step_name}.html"
    html_path = os.path.join("screenshots", html_filename)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print(f"[📄] Saved HTML dump: {html_path}")


def solve_math_challenge(driver):
    """Detect and solve simple math challenge if it appears."""
    try:
        challenge_box = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "form input[type='text']"))
        )
        question_text = driver.find_element(By.CSS_SELECTOR, "form").text.strip()
        print(f"[*] Math challenge detected: {question_text}")

        # Try to capture with operator
        match = re.search(r"(\d+)\s*([+\-*/])\s*(\d+)", question_text)

        if match:
            a, op, b = int(match.group(1)), match.group(2), int(match.group(3))
        else:
            # Fallback: just numbers, e.g. "1 1 =" or "5 3 ="
            nums = re.findall(r"\d+", question_text)
            if len(nums) == 2:
                a, b = int(nums[0]), int(nums[1])
                if a == b:
                    op = "+"   # assume addition when numbers are equal
                    print(f"[!] No operator found, assuming addition: {a} + {b}")
                else:
                    op = "-"   # assume subtraction otherwise
                    print(f"[!] No operator found, assuming subtraction: {a} - {b}")
            else:
                raise RuntimeError("❌ Could not parse math question.")

        # Solve equation
        if op == "+": answer = a + b
        elif op == "-": answer = a - b
        elif op == "*": answer = a * b
        elif op == "/": answer = a // b if b != 0 else 0
        else: raise RuntimeError(f"Unknown operator {op}")

        challenge_box.clear()
        challenge_box.send_keys(str(answer))
        challenge_box.submit()
        print(f"[+] Solved math challenge: {a} {op} {b} = {answer}")

        _save_screenshot(driver, "step_7_after_math_challenge")
        time.sleep(3)
        return True

    except TimeoutException:
        print("[*] No math challenge detected.")
        return False


# -------------Extract Slots and Save them into CSV-----------
# Toggle here: use UTC or local timezone
USE_UTC = True  

def format_timestamp(ts: float) -> str:
    """
    Convert a POSIX timestamp to a formatted datetime string.
    If USE_UTC=True → timezone-aware UTC datetime.
    Else → system local timezone datetime.
    """
    if USE_UTC:
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    else:
        dt = datetime.fromtimestamp(ts)  # local time
        return dt.strftime("%Y-%m-%d %H:%M %Z")

# --------- Parse Slots data ----------
def parse_slot_text(text: str) -> dict:
    """
    Parse a slot string into structured fields:
    Month, Day, Date, Time, Status.
    """
    try:
        # Try to parse any recognizable datetime
        dt = parser.parse(text, fuzzy=True, dayfirst=True)

        return {
            "month": dt.strftime("%B"),     # March
            "day": dt.strftime("%A"),       # Monday
            "date": dt.strftime("%d"),      # 12
            "time": dt.strftime("%I:%M %p"),# 10:30 AM
            "status": "Available" if "available" in text.lower() else "Full" if "full" in text.lower() else "Unknown",
            "raw": text.strip()
        }
    except Exception:
        # Fallback if parsing fails
        return {
            "month": "",
            "day": "",
            "date": "",
            "time": "",
            "status": "Unknown",
            "raw": text.strip()
        }
    # ================================================
# def save_slots_to_csv(slots, filename="slot_data/slots_history.csv"):
#     """
#     Save extracted slots into CSV with structured fields.
#     """
#     os.makedirs(os.path.dirname(filename), exist_ok=True)
#     file_exists = os.path.isfile(filename)

#     with open(filename, "a", newline="", encoding="utf-8") as f:
#         writer = csv.writer(f)

#         # Write header if file doesn't exist
#         if not file_exists:
#             writer.writerow(["Extracted_At", "Month", "Day", "Date", "Time", "Status", "Raw_Text"])

#         now_str = format_timestamp(datetime.now(timezone.utc).timestamp())

#         for slot in slots:
#             writer.writerow([
#                 now_str,
#                 slot.get("month"),
#                 slot.get("day"),
#                 slot.get("date"),
#                 slot.get("time"),
#                 slot.get("status"),
#                 slot.get("raw")
#             ])

#     print(f"[💾] Saved {len(slots)} slots into {filename}")
def save_slots_to_csv(slots, folder="slot_data"):
    """
    Save extracted slots into daily CSV files with timezone-aware timestamps.
    Each day gets its own CSV: slots_YYYY-MM-DD.csv
    """
    os.makedirs(folder, exist_ok=True)

    # Current UTC/local date string
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d") if USE_UTC \
        else datetime.now().strftime("%Y-%m-%d")

    filename = os.path.join(folder, f"slots_{today}.csv")
    file_exists = os.path.isfile(filename)

    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Write header if file doesn't exist yet
        if not file_exists:
            writer.writerow(["Extracted_At", "Month", "Day", "Date", "Time", "Status"])

        now_str = format_timestamp(datetime.now(timezone.utc).timestamp())

        for slot in slots:
            writer.writerow([
                now_str,
                slot.get("month"),
                slot.get("day"),
                slot.get("date"),
                slot.get("time"),
                slot.get("status")
            ])

    print(f"[💾] Saved {len(slots)} slots into {filename}")

# --------- Extract Slots ----------------
def extract_slots(driver):
    """
    Extract slots from booking calendar.
    Phase 1: Print all months with their slots (available & not available).
    Phase 2: Print available slots only.
    """
    print("[*] Looking for booking calendar...")

    slots = []
    _save_screenshot(driver, "step9_slots_page")

    soup = BeautifulSoup(driver.page_source, "html.parser")
    slot_elements = soup.select(".ss_slot, .slot, table.ss_calendar td")

    for elem in slot_elements:
        text = elem.get_text(strip=True)
        if not text:
            continue

        # Skip junk banners / notices
        if any(skip in text.lower() for skip in [
            "signed in", "notice", "successfully logged in",
            "help", "settings", "sign out"
        ]):
            continue

        slot = {
            "month": "",
            "day": "",
            "date": "",
            "time": "",
            "status": "Not available",
            "raw": text
        }

        # Status
        if "available" in text.lower():
            slot["status"] = "Available"
        elif "full" in text.lower() or "no slots" in text.lower():
            slot["status"] = "Full"

        # Parse date (e.g. "Monday 13 October")
        date_match = re.search(r"([A-Za-z]+)\s+(\d{1,2})\s+([A-Za-z]+)", text)
        time_match = re.search(r"(\d{1,2}:\d{2}\s*(?:AM|PM)?)", text)

        if date_match:
            slot["day"] = date_match.group(1)
            slot["date"] = date_match.group(2)
            slot["month"] = date_match.group(3)

        if time_match:
            slot["time"] = time_match.group(1)

        slots.append(slot)

    # --------------------------
    # Phase 1: Print all months
    # --------------------------
    grouped = defaultdict(list)
    for s in slots:
        grouped[s["month"] or "Unknown"].append(s)

    print("\n📅 All slots (month-wise):")
    for month, items in grouped.items():
        print(f"\n--- {month} ---")
        for s in items:
            print(f"  {s['day']} {s['date']} {s['time']} → {s['status']}")

    # --------------------------
    # Phase 2: Print available slots only
    # --------------------------
    available = [s for s in slots if s["status"] == "Available"]

    print("\n🎉 Available slots:")
    if available:
        for s in available:
            print(f"  {s['day']} {s['date']} {s['month']} {s['time']} → {s['status']}")
    else:
        print("  ❌ No available slots right now.")

    return slots


# def extract_slots(driver):
#     """
#     Extract available slots from booking calendar after login.
#     Only parses real slot elements, skips headers/warnings.
#     """
#     print("[*] Looking for booking calendar...")

#     slots = []
#     _save_screenshot(driver, "step9_slots_page")

#     # Use BeautifulSoup to refine parsing
#     soup = BeautifulSoup(driver.page_source, "html.parser")

#     # --- Look for slot containers ---
#     slot_elements = soup.select(".ss_slot, .slot, table.ss_calendar td")

#     for elem in slot_elements:
#         text = elem.get_text(strip=True)
#         if not text:
#             continue

#         # Skip junk like login banners / notices
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
#             "status": "Unknown",
#             "raw": text
#         }

#         # Extract "Available" or "Full"
#         if "available" in text.lower():
#             slot["status"] = "Available"
#         elif "full" in text.lower() or "no slots" in text.lower():
#             slot["status"] = "Full"

#         # Extract date/time patterns (e.g. "Monday 13 October 12:00")
#         date_match = re.search(r"([A-Za-z]+)\s+(\d{1,2})\s+([A-Za-z]+)", text)
#         time_match = re.search(r"(\d{1,2}:\d{2}\s*(?:AM|PM)?)", text)

#         if date_match:
#             slot["day"] = date_match.group(1)
#             slot["date"] = date_match.group(2)
#             slot["month"] = date_match.group(3)

#         if time_match:
#             slot["time"] = time_match.group(1)

#         slots.append(slot)

#     print(f"[🎉] Found {len(slots)} slot(s) after filtering.")
#     for s in slots[:10]:
#         print("   ", s)

#     return slots



# def extract_slots(driver):
#     """
#     Extract available slots from booking calendar after login.
#     Parses text into structured fields and saves them.
#     """
#     print("[*] Looking for booking calendar...")
#     slots = []

#     def parse_slots(scope_driver, tag="main"):
#         parsed = []
#         rows = scope_driver.find_elements(By.CSS_SELECTOR, "tr, .slot, .ss_slot, td, div")

#         for row in rows:
#             text = row.text.strip()
#             if not text:
#                 continue
#             parsed.append(parse_slot_text(text))

#         if parsed:
#             print(f"[+] Extracted {len(parsed)} slots from {tag}")
#         return parsed

#     # Try main DOM
#     slots = parse_slots(driver, "main DOM")
#     if not slots:
#         iframes = driver.find_elements(By.TAG_NAME, "iframe")
#         print(f"[*] Found {len(iframes)} iframes after login")
#         for idx, iframe in enumerate(iframes):
#             try:
#                 driver.switch_to.frame(iframe)
#                 iframe_slots = parse_slots(driver, f"iframe#{idx}")
#                 if iframe_slots:
#                     slots.extend(iframe_slots)
#                     _save_screenshot(driver, f"step9_slots_found_iframe{idx}")
#                     driver.switch_to.default_content()
#                     break
#             except Exception as e:
#                 print(f"[!] Error scanning iframe #{idx}: {e}")
#             finally:
#                 driver.switch_to.default_content()

#     if slots:
#         _save_screenshot(driver, "step9_slots_found_main")
#         save_slots_to_csv(slots)   # ✅ Save structured slots here

#         # Pretty print in table
#         table = [
#             [s["month"], s["day"], s["date"], s["time"], s["status"]]
#             for s in slots
#         ]
#         print("\n📅 Extracted Slots:\n")
#         print(tabulate(table, headers=["Month", "Day", "Date", "Time", "Status"], tablefmt="grid"))

#         return slots

#     print("[❌] Could not find any slots.")
#     _save_screenshot(driver, "step9_slots_not_found")
#     return []


# def extract_slots(driver):
#     """
#     Extract available slots from booking calendar after login.
#     Parses text into structured fields and saves them.
#     """
#     print("[*] Looking for booking calendar...")
#     slots = []

#     def parse_slots(scope_driver, tag="main"):
#         parsed = []
#         rows = scope_driver.find_elements(By.CSS_SELECTOR, "tr, .slot, .ss_slot, td, div")

#         for row in rows:
#             text = row.text.strip()
#             if not text:
#                 continue
#             parsed.append(parse_slot_text(text))

#         if parsed:
#             print(f"[+] Extracted {len(parsed)} slots from {tag}")
#         return parsed

#     # Try main DOM
#     slots = parse_slots(driver, "main DOM")
#     if not slots:
#         iframes = driver.find_elements(By.TAG_NAME, "iframe")
#         print(f"[*] Found {len(iframes)} iframes after login")
#         for idx, iframe in enumerate(iframes):
#             try:
#                 driver.switch_to.frame(iframe)
#                 iframe_slots = parse_slots(driver, f"iframe#{idx}")
#                 if iframe_slots:
#                     slots.extend(iframe_slots)
#                     _save_screenshot(driver, f"step9_slots_found_iframe{idx}")
#                     driver.switch_to.default_content()
#                     break
#             except Exception as e:
#                 print(f"[!] Error scanning iframe #{idx}: {e}")
#             finally:
#                 driver.switch_to.default_content()

#     if slots:
#         _save_screenshot(driver, "step9_slots_found_main")
#         save_slots_to_csv(slots)   # ✅ Save structured slots here
#         return slots

#     print("[❌] Could not find any slots.")
#     _save_screenshot(driver, "step9_slots_not_found")
#     return []


# def extract_slots(driver):
#     """
#     Extract available slots from booking calendar after login.
#     Searches main DOM and all iframes.
#     Returns a list of (text, status).
#     """
#     print("[*] Looking for booking calendar...")

#     slots = []

#     def parse_slots(scope_driver, tag="main"):
#         """Helper: parse slots from given DOM scope."""
#         parsed = []
#         rows = scope_driver.find_elements(By.CSS_SELECTOR, "tr, .slot, .ss_slot, td, div")

#         for row in rows:
#             text = row.text.strip()
#             if not text:
#                 continue

#             if "Available" in text or "available" in text.lower():
#                 parsed.append({"slot": text, "status": "Available"})
#             elif "Full" in text or "No slots" in text:
#                 parsed.append({"slot": text, "status": "Full"})
#             elif re.search(r"\d{1,2}:\d{2}", text):  # time like 10:30
#                 parsed.append({"slot": text, "status": "Unknown"})

#         if parsed:
#             print(f"[+] Extracted {len(parsed)} slots from {tag}")
#         return parsed

#     # --- Try main DOM first ---
#     slots = parse_slots(driver, "main DOM")
#     if slots:
#         _save_screenshot(driver, "step9_slots_found_main")
#         return slots

#     # --- Check all iframes ---
#     iframes = driver.find_elements(By.TAG_NAME, "iframe")
#     print(f"[*] Found {len(iframes)} iframes after login")
#     for idx, iframe in enumerate(iframes):
#         try:
#             driver.switch_to.frame(iframe)
#             iframe_slots = parse_slots(driver, f"iframe#{idx}")
#             if iframe_slots:
#                 slots.extend(iframe_slots)
#                 _save_screenshot(driver, f"step9_slots_found_iframe{idx}")
#                 driver.switch_to.default_content()
#                 return slots
#         except Exception as e:
#             print(f"[!] Error scanning iframe #{idx}: {e}")
#         finally:
#             driver.switch_to.default_content()

#     # --- If nothing found ---
#     print("[❌] Could not find any slots in main DOM or iframes.")
#     _save_screenshot(driver, "step9_slots_not_found")
#     return slots



# ------- Login Function --------

def login(driver, username: str = EMAIL, password: str = PASSWORD, headless=False):
    """Single login attempt flow with slot extraction."""
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

    email_box.clear()
    email_box.send_keys(username)
    _human_sleep()
    password_box.clear()
    password_box.send_keys(password)
    _human_sleep()
    _save_screenshot(driver, "step5_filled_login")

    try:
        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_btn.click()
        print("[+] Clicked submit button")
    except Exception:
        password_box.send_keys("\n")

    time.sleep(3)
    _save_screenshot(driver, "step6_after_submit")

    # ---- Solve Math Challenge if needed ----
    solve_math_challenge(driver)

    # ---- Post-login validation ----
    try:
        WebDriverWait(driver, 15).until(
            lambda d: "Log out" in d.page_source or "Available" in d.page_source
        )
        print("[✅] Logged in successfully, slots page available.")
        _save_screenshot(driver, "step8_logged_in")

        # Extract slots
        slots = extract_slots(driver)
        if slots:
            available = [s for s in slots if s["status"] == "Available"]
            if available:
                print(f"[🎉] Found {len(available)} available slots!")
            else:
                print("[ℹ️] No available slots right now.")
        return True

    except TimeoutException:
        print("[❌] Login failed or slots page not found.")
        _save_screenshot(driver, "step8_login_failed")
        return False


# ======================================================================
# import os
# import time
# import random
# import re
# from datetime import datetime
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException

# from config.settings import EMAIL, PASSWORD, MAX_LOGIN_ATTEMPTS, SAVE_SCREENSHOTS


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
#         question_text = driver.find_element(By.CSS_SELECTOR, "form").text
#         print(f"[*] Math challenge detected: {question_text}")

#         import re
#         # Try "6 - 4 =" or "1 + 1 ="
#         match = re.search(r"(\d+)\s*([+\-*/])\s*(\d+)", question_text)

#         if match:
#             a, op, b = int(match[1]), match[2], int(match[3])
#         else:
#             # Try "5 3 =" (no operator → assume subtraction)
#             nums = re.findall(r"\d+", question_text)
#             if len(nums) == 2:
#                 a, b = int(nums[0]), int(nums[1])
#                 op = "-"  # default assumption
#                 print(f"[!] No operator found, defaulting to subtraction: {a} - {b}")
#             else:
#                 raise RuntimeError("❌ Could not parse math question.")

#         # Solve equation
#         if op == "+": answer = a + b
#         elif op == "-": answer = a - b
#         elif op == "*": answer = a * b
#         elif op == "/": answer = a // b
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

# def extract_slots(driver):
#     """
#     Extract available slots from booking calendar after login.
#     Returns a list of (date, time, status).
#     """
#     print("[*] Looking for booking calendar...")

#     try:
#         # Wait for calendar/table to load
#         calendar = WebDriverWait(driver, 20).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, ".ss_calendar, table, .slots"))
#         )
#         _save_screenshot(driver, "step9_slots_page")

#         # Collect all rows/cells with slot info
#         slots = []
#         rows = driver.find_elements(By.CSS_SELECTOR, "tr, .slot, .ss_slot")

#         for row in rows:
#             text = row.text.strip()
#             if not text:
#                 continue

#             # Detect "Available" or "Full"
#             if "Available" in text or "available" in text.lower():
#                 slots.append({"slot": text, "status": "Available"})
#             elif "Full" in text or "No slots" in text:
#                 slots.append({"slot": text, "status": "Full"})
#             else:
#                 # Generic fallback
#                 slots.append({"slot": text, "status": "Unknown"})

#         print(f"[+] Extracted {len(slots)} slot entries")
#         for s in slots[:10]:  # print only first 10
#             print("   ", s)

#         return slots

#     except TimeoutException:
#         print("[❌] Could not find booking calendar on page.")
#         _save_screenshot(driver, "step9_slots_not_found")
#         return []


# def login(driver, username: str = EMAIL, password: str = PASSWORD, headless=False):
#     """Main login flow with retry + exponential backoff."""
#     root = "https://schedule.cf-grcon-isl-pakistan.com/"

#     max_attempts = int(MAX_LOGIN_ATTEMPTS) if MAX_LOGIN_ATTEMPTS is not None else 3
#     for attempt in range(1, max_attempts + 1):
#         print(f"\n[🔁] Login attempt {attempt}/{MAX_LOGIN_ATTEMPTS}")
#         driver.get(root)
#         _save_screenshot(driver, f"attempt{attempt}_step1_home")

#         # ---- Handle Turnstile ----
#         print("[*] Waiting for Turnstile or redirect...")
#         try:
#             WebDriverWait(driver, 20).until(
#                 lambda d: "/landing/home" in d.current_url or len(d.find_elements(By.TAG_NAME, "iframe")) > 0
#             )
#         except Exception:
#             pass
#         _save_screenshot(driver, f"attempt{attempt}_step2_turnstile")

#         if "/landing/home" not in driver.current_url:
#             print("[!] Could not auto-pass Turnstile. Solve manually if visible.")
#             if headless:
#                 raise RuntimeError("Headless=True but manual Turnstile solve required. Use headless=False.")
#             else:
#                 print("[*] Waiting up to 2 minutes for manual Turnstile solve...")
#                 try:
#                     WebDriverWait(driver, 120).until(
#                         lambda d: "/landing/home" in d.current_url or "National visa for WORK" in d.page_source
#                     )
#                     print("[+] Turnstile solved manually → category page loaded ✅")
#                 except Exception:
#                     raise RuntimeError("Turnstile not solved in time.")
#         _save_screenshot(driver, f"attempt{attempt}_step3_category")

#         # ---- Category Page ----
#         try:
#             work_link = WebDriverWait(driver, 30).until(
#                 EC.presence_of_element_located((By.LINK_TEXT, "National visa for WORK"))
#             )
#             try:
#                 work_link.click()
#                 print("[+] Clicked 'National visa for WORK' link")
#             except Exception:
#                 print("[!] Normal click failed, trying ActionChains...")
#                 actions = ActionChains(driver)
#                 actions.move_to_element(work_link).pause(0.5).click().perform()
#                 print("[+] Clicked link using ActionChains")
#             _human_sleep(2, 3)
#         except Exception as e:
#             raise RuntimeError(f"❌ Could not click 'National visa for WORK': {e}")
#         _save_screenshot(driver, f"attempt{attempt}_step4_after_work_click")

#         # ---- Login Form ----
#         try:
#             email_box = WebDriverWait(driver, 20).until(
#                 EC.presence_of_element_located((By.ID, "name"))
#             )
#             password_box = WebDriverWait(driver, 20).until(
#                 EC.presence_of_element_located((By.ID, "password"))
#             )
#             print("[+] Found login form fields")
#         except TimeoutException:
#             _save_screenshot(driver, f"attempt{attempt}_step5_login_form_not_found")
#             continue

#         email_box.clear()
#         email_box.send_keys(username)
#         _human_sleep()
#         password_box.clear()
#         password_box.send_keys(password)
#         _human_sleep()
#         _save_screenshot(driver, f"attempt{attempt}_step5_filled_login")

#         try:
#             submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
#             submit_btn.click()
#             print("[+] Clicked submit button")
#         except Exception:
#             password_box.send_keys("\n")

#         time.sleep(3)
#         _save_screenshot(driver, f"attempt{attempt}_step6_after_submit")

#         # ---- Solve Math Challenge if needed ----
#         solve_math_challenge(driver)

#         # ---- Post-login validation ----
#         try:
#             WebDriverWait(driver, 15).until(
#                 lambda d: "Log out" in d.page_source or "Available slots" in d.page_source
#             )
#             print("[✅] Logged in successfully, slots page available.")
#             _save_screenshot(driver, f"attempt{attempt}_step8_logged_in")
#             return True
#         except TimeoutException:
#             print("[❌] Login failed or slots page not found.")
#             _save_screenshot(driver, f"attempt{attempt}_step8_login_failed")

#             # Exponential backoff with random jitter
#             base_delay = 5 * (2 ** (attempt - 1))  # 5s → 10s → 20s
#             jitter = random.uniform(0, 2 + attempt)  # small randomness
#             wait_time = base_delay + jitter
#             print(f"[*] Waiting {wait_time:.1f}s before retrying...")
#             time.sleep(wait_time)

#     raise RuntimeError("❌ All login attempts failed.")



# ====================================================================
# import os
# import time
# import random
# from datetime import datetime
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException
# from config import settings


# def _human_sleep(min_s=0.4, max_s=1.2):
#     """Sleep randomly to simulate human typing delays."""
#     time.sleep(random.uniform(min_s, max_s))


# def save_debug(driver, step_name: str):
#     """Save screenshot + HTML dump if SAVE_DEBUG=True."""
#     if not settings.SAVE_DEBUG:
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


# def login(driver, headless=False, max_retries: int = 3):
#     root = settings.SITE_URL
#     print("[*] Opening homepage:", root)
#     driver.get(root)
#     save_debug(driver, "step_1_home")

#     # ---- Handle Turnstile ----
#     print("[*] Waiting for Turnstile or redirect...")
#     try:
#         WebDriverWait(driver, 20).until(
#             lambda d: "/landing/home" in d.current_url
#             or len(d.find_elements(By.TAG_NAME, "iframe")) > 0
#         )
#     except Exception:
#         pass
#     save_debug(driver, "step_2_turnstile")

#     if "/landing/home" in driver.current_url:
#         print("[+] Already passed Turnstile -> on landing/home ✅")
#     else:
#         print("[!] Could not auto-pass Turnstile. Solve manually if visible.")
#         if headless:
#             raise RuntimeError("Headless=True but manual Turnstile solve required. Use headless=False.")
#         else:
#             print("[*] Waiting up to 2 minutes for manual Turnstile solve...")
#             try:
#                 WebDriverWait(driver, 120).until(
#                     lambda d: "/landing/home" in d.current_url
#                     or "National visa for WORK" in d.page_source
#                 )
#                 print("[+] Turnstile solved manually → category page loaded ✅")
#             except Exception:
#                 raise RuntimeError("Turnstile not solved in time.")
#     save_debug(driver, "step_3_category")

#     # ---- Category Page ----
#     print("[*] Waiting for category options...")
#     try:
#         work_link = WebDriverWait(driver, 30).until(
#             EC.presence_of_element_located((By.LINK_TEXT, "National visa for WORK"))
#         )
#         try:
#             work_link.click()
#             print("[+] Clicked 'National visa for WORK' link")
#         except Exception:
#             print("[!] Normal click failed, trying ActionChains...")
#             actions = ActionChains(driver)
#             actions.move_to_element(work_link).pause(0.5).click().perform()
#             print("[+] Clicked link using ActionChains")
#         _human_sleep(2, 3)
#     except Exception as e:
#         raise RuntimeError(f"❌ Could not click 'National visa for WORK': {e}")
#     save_debug(driver, "step_4_after_work_click")

#     # ---- Retry loop for login ----
#     for attempt in range(1, max_retries + 1):
#         print(f"[*] Attempt {attempt}/{max_retries} to log in...")

#         try:
#             email_box = WebDriverWait(driver, 20).until(
#                 EC.presence_of_element_located((By.ID, "name"))
#             )
#             # email_box = WebDriverWait(driver, 20).until(
#             #     EC.element_to_be_clickable((By.ID, "email")))
#             password_box = WebDriverWait(driver, 20).until(
#                 EC.presence_of_element_located((By.NAME, "password"))
#             )
#             print("[+] Found login form fields")

#             # Fill form
#             email_box.clear()
#             email_box.send_keys(settings.EMAIL)
#             _human_sleep()
#             password_box.clear()
#             password_box.send_keys(settings.PASSWORD)
#             _human_sleep()
#             save_debug(driver, f"step_5_filled_login_attempt{attempt}")

#             # Submit
#             try:
#                 submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
#                 submit_btn.click()
#                 print("[+] Clicked submit button")
#             except Exception:
#                 print("[!] Could not find submit button. Pressing Enter on password field.")
#                 password_box.send_keys("\n")

#             # ---- Post-login Validation ----
#             try:
#                 WebDriverWait(driver, 60).until(
#                     EC.any_of(
#                         EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'Log out')]")),
#                         EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Available slots')]")),
#                         EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Welcome')]")),
#                         EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Dashboard')]")),
#                         EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Booking')]")),
#                     )
#                 )
#                 save_debug(driver, f"step_6_login_success_attempt{attempt}")
#                 print("[✅] Login successful!")
#                 return True
#             except TimeoutException:
#                 # Detect error banners
#                 error_text = ""
#                 try:
#                     err = driver.find_element(By.CSS_SELECTOR, ".alert-danger, .error, .login-error")
#                     error_text = err.text.strip()
#                 except NoSuchElementException:
#                     if "invalid login" in driver.page_source.lower():
#                         error_text = "Invalid login name or password (found in page)"
#                 save_debug(driver, f"step_6_login_failed_attempt{attempt}")
#                 print(f"[❌] Login failed on attempt {attempt}. Server message: {error_text}")

#                 if attempt < max_retries:
#                     base_backoff = 5 * (2 ** (attempt - 1))  # 5, 10, 20
#                     jitter = random.uniform(1.0, 1.3)        # add +0–30%
#                     wait_time = int(base_backoff * jitter)
#                     print(f"[*] Retrying after ~{wait_time} seconds...")
#                     driver.refresh()
#                     time.sleep(wait_time)
#                     continue
#                 else:
#                     return False

#         except TimeoutException:
#             save_debug(driver, f"step_5_login_form_not_found_attempt{attempt}")
#             print(f"[❌] Login form not found on attempt {attempt}.")
#             if attempt < max_retries:
#                 base_backoff = 5 * (2 ** (attempt - 1))
#                 jitter = random.uniform(1.0, 1.3)
#                 wait_time = int(base_backoff * jitter)
#                 print(f"[*] Retrying after ~{wait_time} seconds...")
#                 driver.refresh()
#                 time.sleep(wait_time)
#                 continue
#             else:
#                 return False
