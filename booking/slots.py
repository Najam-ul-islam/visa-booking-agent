# import os, csv
# from selenium.webdriver.common.by import By
# from .utils import _human_sleep, _save_screenshot
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException
# from collections import defaultdict
# from datetime import datetime, timezone

# SLOTS_DIR = "slots_history"
# os.makedirs(SLOTS_DIR, exist_ok=True)

# # ANSI colors
# GREY = "\033[90m"
# RED = "\033[91m"
# RESET = "\033[0m"
# WEEKEND_SKIP = {"FRI", "SAT", "SUN"}  # skip weekends in CSV


# # ---------------- Calendar Extraction ----------------

# def extract_slots(driver, months_ahead: int = 4):
#     """
#     Extract booking slots from the calendar:
#     - Loops through a fixed number of months (default = 5).
#     - Falls back to 'Available' view if month slots are not found.
#     - Skips Fri/Sat/Sun when saving to CSV (but still highlights them grey in console).
#     Returns a list of slot dicts.
#     """
#     slots = []

#     def parse_month_slots(month_label):
#         parsed = []
#         try:
#             WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "div.month"))
#             )
#             month_container = driver.find_element(By.CSS_SELECTOR, "div.month")

#             # Extract weekday headers
#             weekday_headers = month_container.find_elements(By.CSS_SELECTOR, "thead th")
#             weekdays = [w.text.strip() for w in weekday_headers if w.text.strip()]

#             # Extract day cells
#             day_cells = month_container.find_elements(By.CSS_SELECTOR, "tbody td")
#             for idx, cell in enumerate(day_cells):
#                 day_num = cell.text.strip()
#                 classes = cell.get_attribute("class")

#                 if not day_num or "other" in classes:
#                     continue  # skip empty/other-month days

#                 # Map index → weekday (skip leftbar cells)
#                 weekday = weekdays[(idx % 8) - 1] if (idx % 8) != 0 else None
#                 if not weekday:
#                     continue

#                 # Status mapping
#                 if "busy" in classes:
#                     status = "Unavailable"
#                 elif "closed" in classes:
#                     status = "Closed"
#                 else:
#                     status = "Available"

#                 parsed.append({
#                     "view": "Month",
#                     "month": month_label,
#                     "day": day_num,
#                     "weekday": weekday,
#                     "status": status
#                 })

#             # Save screenshot
#             _save_screenshot(driver, f"calendar_{month_label.replace(' ', '_')}")

#         except Exception as e:
#             print(f"[!] Error parsing month {month_label}: {e}")

#         return parsed

#     def parse_available_view():
#         parsed = []
#         try:
#             WebDriverWait(driver, 5).until(
#                 EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".achip"))
#             )
#             slot_divs = driver.find_elements(By.CSS_SELECTOR, ".achip")
#             for slot in slot_divs:
#                 time_text = slot.text.strip()
#                 parsed.append({
#                     "view": "Available",
#                     "month": None,
#                     "day": None,
#                     "weekday": None,
#                     "time": time_text,
#                     "status": "Available"
#                 })
#         except TimeoutException:
#             print("[⚠️] No slots found in available view.")
#         return parsed

#     print("[*] Looking for booking calendar...")

#     # 🔹 Step 1: Month view (loop fixed number of months)
#     try:
#         month_btn = driver.find_element(By.XPATH, "//li[contains(text(),'Month')]")
#         driver.execute_script("arguments[0].click();", month_btn)
#         _human_sleep(1, 2)
#         print("[+] Switched to month view")

#         for i in range(months_ahead):
#             # Get current month label
#             month_label = driver.find_element(By.CSS_SELECTOR, ".month .mid").text.strip()
#             print(f"[📅] Scanning {month_label} ({i+1}/{months_ahead})")

#             slots.extend(parse_month_slots(month_label))

#             # Try to go to next month
#             try:
#                 next_btn = driver.find_element(By.CSS_SELECTOR, ".navhead .i-r")
#                 driver.execute_script("arguments[0].click();", next_btn)
#                 _human_sleep(2, 3)
#             except Exception:
#                 print("[ℹ️] No more months available.")
#                 break
#     except Exception as e:
#         print(f"[!] Could not switch to month view: {e}")

#     # 🔹 Step 2: Available view fallback
#     try:
#         avail_btn = driver.find_element(By.XPATH, "//li[contains(text(),'Available')]")
#         driver.execute_script("arguments[0].click();", avail_btn)
#         _human_sleep(1, 2)
#         print("[+] Switched to available view")
#         slots.extend(parse_available_view())
#     except Exception as e:
#         print(f"[!] Could not switch to available view: {e}")

#     # Summary
#     if slots:
#         print_slots_grouped(slots)
#     else:
#         print("[⚠️] No slots extracted.")
#     return slots


# # ---------------- CSV Saving ----------------

# def save_slots_to_csv(slots, filename="slots_history/slots_history.csv"):
#     """
#     Save extracted slots into CSV file with timezone-aware timestamp.
#     Weekends are skipped for saving.
#     """
#     os.makedirs(os.path.dirname(filename), exist_ok=True)
#     file_exists = os.path.isfile(filename)

#     with open(filename, "a", newline="", encoding="utf-8") as f:
#         writer = csv.writer(f)
#         if not file_exists:
#             writer.writerow(["Extracted_At", "Date", "Weekday", "Time", "Status", "View"])

#         now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

#         for s in slots:
#             weekday = (s.get("weekday") or "?").upper()
#             if weekday in WEEKEND_SKIP:
#                 continue  # skip weekends for saving

#             writer.writerow([
#                 now_str,
#                 s.get("date", ""),
#                 s.get("weekday", ""),
#                 s.get("time", ""),
#                 s.get("status", ""),
#                 s.get("view", "")
#             ])

#     saved_count = len([s for s in slots if (s.get("weekday") or "").upper() not in WEEKEND_SKIP])
#     print(f"[💾] Saved {saved_count} weekday slots → {filename}")


# # ---------------- Console Printing ----------------

# def print_slots_grouped(slots):
#     """Pretty print slots grouped by month. Highlight weekends in grey, skip in CSV."""
#     if not slots:
#         print("[⚠️] No slots extracted this run.")
#         return

#     grouped = defaultdict(list)
#     for s in slots:
#         month_label = s.get("date", "?").split()[0] if s.get("date") else "?"
#         grouped[month_label].append(s)

#     print("\n📅 All slots (month-wise):")
#     for month, month_slots in grouped.items():
#         print(f"\n  {month}:")
#         for s in month_slots:
#             weekday = (s.get("weekday") or "?").upper()
#             if weekday in WEEKEND_SKIP:
#                 print(f"    {GREY}{s.get('date','?')} ({s.get('weekday','?')}) {s.get('time','?')} → {s.get('status','?')} [Weekend]{RESET}")
#             else:
#                 print(f"    {s.get('date','?')} ({s.get('weekday','?')}) {s.get('time','?')} → {s.get('status','?')}")

#     print("\n🎉 Available slots (weekdays only):")
#     available = [s for s in slots if s.get("status") == "Available" and (s.get("weekday") or "").upper() not in WEEKEND_SKIP]
#     if available:
#         for s in available:
#             print(f"  {s.get('date','?')} ({s.get('weekday','?')}) {s.get('time','?')} → Available")
#     else:
#         print("  ❌ No available weekday slots right now.")

# =================================================================================================
# --------------------- WORKING UPDATED CODE -----------------------

import os, csv
from selenium.webdriver.common.by import By
from .utils import _human_sleep, _save_screenshot
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from collections import defaultdict
from datetime import datetime, timezone

SLOTS_DIR = "slots_history"
os.makedirs(SLOTS_DIR, exist_ok=True)

# ANSI colors
GREY = "\033[90m"
RESET = "\033[0m"
WEEKEND_SKIP = {"FRI", "SAT", "SUN"}  # skip weekends in CSV


# ---------------- Calendar Extraction ----------------

def extract_slots(driver, months_ahead: int = 5):
    """
    Extract booking slots from the calendar:
    - Loops through a fixed number of months (default = 5).
    - Skips Fri/Sat/Sun when saving to CSV (but still highlights them grey in console).
    Returns a list of slot dicts.
    """
    slots = []

    def parse_month_slots(month_label):
        parsed = []
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.month"))
            )
            month_container = driver.find_element(By.CSS_SELECTOR, "div.month")

            # Extract weekday headers (Sun–Sat)
            weekday_headers = month_container.find_elements(By.CSS_SELECTOR, "thead th")
            weekdays = [w.text.strip() for w in weekday_headers if w.text.strip()]

            # Extract day cells
            day_cells = month_container.find_elements(By.CSS_SELECTOR, "tbody td")
            for idx, cell in enumerate(day_cells):
                day_num = cell.text.strip()
                classes = cell.get_attribute("class")

                if not day_num or "other" in classes:
                    continue  # skip empty or other-month days

                # Map index → weekday (skip first column = leftbar)
                weekday = weekdays[(idx % 8) - 1] if (idx % 8) != 0 else None
                if not weekday:
                    continue

                # Status mapping
                if "busy" in classes:
                    status = "Unavailable"
                elif "closed" in classes:
                    status = "Closed"
                else:
                    status = "Available"

                # Full date like "18 September 2025"
                full_date = f"{day_num} {month_label}"

                parsed.append({
                    "view": "Month",
                    "date": full_date,
                    "month": month_label,
                    "day": day_num,
                    "weekday": weekday,
                    "time": "-",  # month view shows only daily availability
                    "status": status
                })

            # Save screenshot for this month
            _save_screenshot(driver, f"calendar_{month_label.replace(' ', '_')}")

        except Exception as e:
            print(f"[!] Error parsing month {month_label}: {e}")

        return parsed

    print("[*] Looking for booking calendar...")

    # 🔹 Step 1: Month view (loop fixed number of months)
    try:
        month_btn = driver.find_element(By.XPATH, "//li[contains(text(),'Month')]")
        driver.execute_script("arguments[0].click();", month_btn)
        _human_sleep(1, 2)
        print("[+] Switched to month view")

        for i in range(months_ahead):
            # Get current month label (e.g., "September 2025")
            month_label = driver.find_element(By.CSS_SELECTOR, ".month .mid").text.strip()
            print(f"[📅] Scanning {month_label} ({i+1}/{months_ahead})")

            slots.extend(parse_month_slots(month_label))

            # Try to go to next month
            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, ".navhead .i-r")
                driver.execute_script("arguments[0].click();", next_btn)
                _human_sleep(2, 3)
            except Exception:
                print("[ℹ️] No more months available.")
                break
    except Exception as e:
        print(f"[!] Could not switch to month view: {e}")

    # Summary
    if slots:
        print_slots_grouped(slots)
    else:
        print("[⚠️] No slots extracted.")
    return slots


# ---------------- CSV Saving ----------------

def save_slots_to_csv(slots, filename="slots_history/slots_history.csv"):
    """
    Save extracted slots into CSV file with timezone-aware timestamp.
    Weekends are skipped for saving.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    file_exists = os.path.isfile(filename)

    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Extracted_At", "Date", "Weekday", "Time", "Status", "View"])

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        for s in slots:
            weekday = (s.get("weekday") or "?").upper()
            if weekday in WEEKEND_SKIP:
                continue  # skip weekends for saving

            writer.writerow([
                now_str,
                s.get("date", ""),
                s.get("weekday", ""),
                s.get("time", ""),
                s.get("status", ""),
                s.get("view", "")
            ])

    saved_count = len([s for s in slots if (s.get("weekday") or "").upper() not in WEEKEND_SKIP])
    print(f"[💾] Saved {saved_count} weekday slots → {filename}")


# ---------------- Console Printing ----------------

def print_slots_grouped(slots):
    """Pretty print slots grouped by month. Highlight weekends in grey, skip in CSV."""
    if not slots:
        print("[⚠️] No slots extracted this run.")
        return

    grouped = defaultdict(list)
    for s in slots:
        grouped[s.get("month", "?")].append(s)

    print("\n📅 All slots (month-wise):")
    for month, month_slots in grouped.items():
        print(f"\n  {month}:")
        for s in month_slots:
            weekday = (s.get("weekday") or "?").upper()
            if weekday in WEEKEND_SKIP:
                print(f"    {GREY}{s.get('date','?')} ({s.get('weekday','?')}) {s.get('time','?')} → {s.get('status','?')} [Weekend]{RESET}")
            else:
                print(f"    {s.get('date','?')} ({s.get('weekday','?')}) {s.get('time','?')} → {s.get('status','?')}")

    print("\n🎉 Available slots (weekdays only):")
    available = [s for s in slots if s.get("status") == "Available" and (s.get("weekday") or "").upper() not in WEEKEND_SKIP]
    if available:
        for s in available:
            print(f"  {s.get('date','?')} ({s.get('weekday','?')}) {s.get('time','?')} → Available")
    else:
        print("  ❌ No available weekday slots right now.")
# ===========================================================================================