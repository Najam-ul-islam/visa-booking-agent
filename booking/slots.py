# import time
# import os, csv
# from selenium.webdriver.common.by import By
# from .utils import _human_sleep, _save_screenshot
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException
# from collections import defaultdict
# from datetime import datetime, timezone


# SLOTS_DIR = "slots_history"
# # ANSI colors
# GREY = "\033[90m"
# RED = "\033[91m"
# RESET = "\033[0m"
# WEEKEND_SKIP = {"FRI", "SAT", "SUN"}  # skip these in CSV
# os.makedirs(SLOTS_DIR, exist_ok=True)


# def switch_to_calendar_view(driver, view_name: str) -> bool:
#     """
#     Switch the booking calendar view by clicking the dropdown option.
#     view_name: "month", "week", "day", or "free" (Available).
#     """
#     try:
#         # Open dropdown
#         trigger = WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((By.ID, "trigger"))
#         )
#         trigger.click()
#         time.sleep(1)

#         # Click the <li> option
#         option = WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((By.XPATH, f"//ul[@class='ts']/li[contains(@onclick,\"{view_name}\")]"))
#         )
#         driver.execute_script("arguments[0].click();", option)
#         print(f"[+] Switched calendar to '{view_name}' view")

#         # Wait for slots to reload
#         time.sleep(3)
#         return True

#     except Exception as e:
#         print(f"[❌] Could not switch to {view_name} view: {e}")
#         return False



# def extract_slots_from_view(driver, view_name: str):
#     """
#     Extract slots from the current calendar view (Month/Available/etc).
#     Returns a list of slot dicts.
#     """
#     slots = []
#     _save_screenshot(driver, f"step9_slots_{view_name.lower()}")

#     rows = driver.find_elements(By.CSS_SELECTOR, ".achip .head")
#     for row in rows:
#         text = row.text.strip()
#         if not text:
#             continue
#         slots.append({
#             "view": view_name,
#             "date": datetime.now().strftime("%Y-%m-%d"),
#             "time": text,
#             "status": "Available" if "Available" in text else "Unknown"
#         })

#     print(f"[📅] {view_name} view → found {len(slots)} slot(s)")
#     return slots


# def get_calendar_slots(driver):
#     """Try Month view first, then fallback to Available view."""
#     all_slots = []

#     try:
#         # 🔹 Switch to month view
#         month_tab = driver.find_element(By.XPATH, "//li[contains(., 'Month')]")
#         driver.execute_script("arguments[0].click();", month_tab)
#         time.sleep(2)
#         print("[+] Switched to month view")
#         month_slots = extract_slots(driver, view="Month")
#         all_slots.extend(month_slots)

#     except Exception as e:
#         print(f"[!] Could not switch to month view: {e}")

#     try:
#         # 🔹 Switch to available view
#         free_tab = driver.find_element(By.XPATH, "//li[contains(., 'Available')]")
#         driver.execute_script("arguments[0].click();", free_tab)
#         time.sleep(2)
#         print("[+] Switched to available view")
#         avail_slots = extract_slots(driver, view="Available")
#         all_slots.extend(avail_slots)

#     except Exception as e:
#         print(f"[!] Could not switch to available view: {e}")

#     print_slots_grouped(all_slots)
#     return all_slots


# def extract_slots(driver):
#     """
#     Extract booking slots from calendar:
#     - Month view: white = Available, blue = Unavailable, skip Fri/Sat/Sun
#     - Available view: fallback if month view is empty
#     Returns a list of slot dicts.
#     """
#     slots = []

#     def parse_month_slots():
#         parsed = []
#         try:
#             WebDriverWait(driver, 10).until(
#                 EC.presence_of_all_elements_located((By.CSS_SELECTOR, "td .inday"))
#             )
#             days = driver.find_elements(By.CSS_SELECTOR, "td .inday")

#             for day in days:
#                 # Get weekday name
#                 try:
#                     weekday_elem = day.find_element(By.XPATH, "./ancestor::td/preceding::tr[@class='dayHeading'][1]/th[position()=count(ancestor::td/preceding-sibling::td)+1]")
#                     weekday = weekday_elem.text.strip()
#                 except Exception:
#                     weekday = ""

#                 # Get date text
#                 try:
#                     date_elem = day.find_element(By.XPATH, "./preceding-sibling::p/span[last()]")
#                     date_text = date_elem.text.strip()
#                 except Exception:
#                     date_text = None

#                 # Loop over slots
#                 slot_divs = day.find_elements(By.CSS_SELECTOR, ".achip")
#                 for slot in slot_divs:
#                     time_text = slot.text.strip()
#                     classes = slot.get_attribute("class")

#                     # Skip Fri/Sat/Sun
#                     if weekday in ["Fri", "Sat", "Sun"]:
#                         continue

#                     # Status: white = Available, blue (with "f") = Unavailable
#                     status = "Unavailable" if "f" in classes else "Available"

#                     parsed.append({
#                         "view": "Month",
#                         "weekday": weekday,
#                         "date": date_text,
#                         "time": time_text,
#                         "status": status
#                     })
#         except TimeoutException:
#             print("[⚠️] No slots found in month view.")
#         return parsed

#     def parse_available_slots():
#         parsed = []
#         try:
#             WebDriverWait(driver, 5).until(
#                 EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".achip"))
#             )
#             slot_divs = driver.find_elements(By.CSS_SELECTOR, ".achip")
#             for slot in slot_divs:
#                 time_text = slot.text.strip()
#                 status = "Available"
#                 parsed.append({
#                     "view": "Available",
#                     "date": None,
#                     "weekday": None,
#                     "time": time_text,
#                     "status": status
#                 })
#         except TimeoutException:
#             print("[⚠️] No slots found in available view.")
#         return parsed

#     print("[*] Looking for booking calendar...")

#     # Step 1: Switch to month view
#     try:
#         month_btn = driver.find_element(By.XPATH, "//li[contains(text(),'Month')]")
#         driver.execute_script("arguments[0].click();", month_btn)
#         _human_sleep(1, 2)
#         print("[+] Switched to month view")
#         slots.extend(parse_month_slots())
#     except Exception as e:
#         print(f"[!] Could not switch to month view: {e}")

#     _save_screenshot(driver, "step9_slots_month")

#     # Step 2: Switch to available view
#     try:
#         avail_btn = driver.find_element(By.XPATH, "//li[contains(text(),'Available')]")
#         driver.execute_script("arguments[0].click();", avail_btn)
#         _human_sleep(1, 2)
#         print("[+] Switched to available view")
#         slots.extend(parse_available_slots())
#     except Exception as e:
#         print(f"[!] Could not switch to available view: {e}")

#     _save_screenshot(driver, "step9_slots_available")

#     # Final summary
#     if slots:
#         print(f"[📅] Extracted {len(slots)} slot(s)")
#         for s in slots[:20]:  # show only first 20 for readability
#             print(f"  {s['date']} ({s['weekday']}) {s['time']} → {s['status']}")
#     else:
#         print("[⚠️] No slots extracted.")

#     return slots


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
#             writer.writerow(["Extracted_At", "Month", "Date", "Weekday", "Time", "Status", "View"])

#         now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

#         for s in slots:
#             if s["weekday"].upper() in WEEKEND_SKIP:
#                 continue  # don't save weekends
#             month_label = s["date"].split()[0] if " " in s["date"] else s["date"]
#             writer.writerow([now_str, month_label, s["date"], s["weekday"], s["time"], s["status"], s["view"]])

#     saved_count = len([s for s in slots if s["weekday"].upper() not in WEEKEND_SKIP])
#     print(f"[💾] Saved {saved_count} weekday slots → {filename}")


# def print_slots_grouped(slots):
#     """Pretty print slots grouped by month. Highlight weekends, but don't skip them in console."""
#     if not slots:
#         print("[⚠️] No slots extracted this run.")
#         return

#     grouped = defaultdict(list)
#     for s in slots:
#         month_label = s["date"].split()[0] if " " in s["date"] else s["date"]
#         grouped[month_label].append(s)

#     print("\n📅 All slots (month-wise):")
#     for month, month_slots in grouped.items():
#         print(f"\n  {month}:")
#         for s in month_slots:
#             if s["weekday"].upper() in WEEKEND_SKIP:
#                 # Grey highlight weekends
#                 print(f"    {GREY}{s['date']} ({s['weekday']}) {s['time']} → {s['status']} [Skipped Weekend]{RESET}")
#             else:
#                 print(f"    {s['date']} ({s['weekday']}) {s['time']} → {s['status']}")

#     print("\n🎉 Available slots (weekdays only):")
#     available = [s for s in slots if s["status"] == "Available" and s["weekday"].upper() not in WEEKEND_SKIP]
#     if available:
#         for s in available:
#             print(f"  {s['date']} ({s['weekday']}) {s['time']} → Available")
#     else:
#         print("  ❌ No available weekday slots right now.")




import time
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
RED = "\033[91m"
RESET = "\033[0m"
WEEKEND_SKIP = {"FRI", "SAT", "SUN"}  # skip weekends in CSV


# ---------------- Calendar Extraction ----------------

# def extract_slots(driver):
#     """
#     Extract booking slots from calendar:
#     - Month view: white = Available, blue = Unavailable
#     - Available view: fallback if month view is empty
#     - Skip Fri/Sat/Sun only in CSV, but show in console
#     """
#     slots = []

#     def parse_month_slots():
#         parsed = []
#         try:
#             WebDriverWait(driver, 10).until(
#                 EC.presence_of_all_elements_located((By.CSS_SELECTOR, "td .inday"))
#             )
#             days = driver.find_elements(By.CSS_SELECTOR, "td .inday")

#             for day in days:
#                 # Weekday header
#                 try:
#                     weekday_elem = day.find_element(
#                         By.XPATH,
#                         "./ancestor::td/preceding::tr[@class='dayHeading'][1]/th[position()=count(ancestor::td/preceding-sibling::td)+1]"
#                     )
#                     weekday = weekday_elem.text.strip().upper()
#                 except Exception:
#                     weekday = "?"

#                 # Date (day number)
#                 try:
#                     date_elem = day.find_element(By.XPATH, "./preceding-sibling::p/span[last()]")
#                     date_text = date_elem.text.strip()
#                 except Exception:
#                     date_text = ""

#                 # Slots in this day
#                 for slot in day.find_elements(By.CSS_SELECTOR, ".achip"):
#                     time_text = slot.text.strip()
#                     classes = slot.get_attribute("class")

#                     status = "Unavailable" if "f" in classes else "Available"

#                     parsed.append({
#                         "view": "Month",
#                         "weekday": weekday,
#                         "date": date_text,
#                         "time": time_text,
#                         "status": status
#                     })
#         except TimeoutException:
#             print("[⚠️] No slots found in month view.")
#         return parsed

#     def parse_available_slots():
#         parsed = []
#         try:
#             WebDriverWait(driver, 5).until(
#                 EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".achip"))
#             )
#             for slot in driver.find_elements(By.CSS_SELECTOR, ".achip"):
#                 time_text = slot.text.strip()
#                 parsed.append({
#                     "view": "Available",
#                     "weekday": "?",
#                     "date": datetime.now().strftime("%Y-%m-%d"),
#                     "time": time_text,
#                     "status": "Available"
#                 })
#         except TimeoutException:
#             print("[⚠️] No slots found in available view.")
#         return parsed

#     print("[*] Looking for booking calendar...")

#     # Month view first
#     try:
#         month_btn = driver.find_element(By.XPATH, "//li[contains(text(),'Month')]")
#         driver.execute_script("arguments[0].click();", month_btn)
#         _human_sleep(1, 2)
#         print("[+] Switched to month view")
#         slots.extend(parse_month_slots())
#     except Exception as e:
#         print(f"[!] Could not switch to month view: {e}")

#     _save_screenshot(driver, "step9_slots_month")

#     # Then available view
#     try:
#         avail_btn = driver.find_element(By.XPATH, "//li[contains(text(),'Available')]")
#         driver.execute_script("arguments[0].click();", avail_btn)
#         _human_sleep(1, 2)
#         print("[+] Switched to available view")
#         slots.extend(parse_available_slots())
#     except Exception as e:
#         print(f"[!] Could not switch to available view: {e}")

#     _save_screenshot(driver, "step9_slots_available")

#     if slots:
#         print(f"[📅] Extracted {len(slots)} slot(s)")
#         for s in slots[:20]:
#             print(f"  {s.get('date','?')} ({s.get('weekday','?')}) {s.get('time','?')} → {s.get('status','?')}")
#     else:
#         print("[⚠️] No slots extracted.")

#     return slots

# def extract_slots(driver):
#     """
#     Extract booking slots from the calendar:
#     - Automatically loops through all available months (until next button is disabled).
#     - Falls back to 'Available' view if month slots are not found.
#     - Skips Fri/Sat/Sun when saving to CSV (but still highlights them grey in console).
#     Returns a list of slot dicts.
#     """
#     slots = []

#     def parse_all_months():
#         parsed = []
#         seen_months = set()

#         while True:
#             try:
#                 WebDriverWait(driver, 10).until(
#                     EC.presence_of_element_located((By.CSS_SELECTOR, "div.month"))
#                 )
#                 month_container = driver.find_element(By.CSS_SELECTOR, "div.month")

#                 # Extract current month label
#                 month_label = month_container.find_element(By.CSS_SELECTOR, ".mid").text.strip()
#                 if month_label in seen_months:
#                     break  # prevent infinite loop
#                 seen_months.add(month_label)

#                 print(f"[📅] Scanning {month_label}")

#                 # Extract weekday headers
#                 weekday_headers = month_container.find_elements(By.CSS_SELECTOR, "thead th")
#                 weekdays = [w.text.strip() for w in weekday_headers if w.text.strip()]

#                 # Extract day cells
#                 day_cells = month_container.find_elements(By.CSS_SELECTOR, "tbody td")
#                 for idx, cell in enumerate(day_cells):
#                     day_num = cell.text.strip()
#                     classes = cell.get_attribute("class")

#                     if not day_num or "other" in classes:
#                         continue  # skip empty/other-month days

#                     # Map index → weekday (skip leftbar cells)
#                     weekday = weekdays[(idx % 8) - 1] if (idx % 8) != 0 else None
#                     if not weekday:
#                         continue

#                     # Status mapping
#                     if "busy" in classes:
#                         status = "Unavailable"
#                     elif "closed" in classes:
#                         status = "Closed"
#                     else:
#                         status = "Available"

#                     parsed.append({
#                         "view": "Month",
#                         "month": month_label,
#                         "day": day_num,
#                         "weekday": weekday,
#                         "status": status
#                     })

#                 # Save screenshot
#                 _save_screenshot(driver, f"calendar_{month_label.replace(' ', '_')}")

#                 # Try next month
#                 try:
#                     next_btn = driver.find_element(By.CSS_SELECTOR, ".navhead .i-r")
#                     if "disabled" in next_btn.get_attribute("class"):
#                         break  # reached the last month
#                     driver.execute_script("arguments[0].click();", next_btn)
#                     _human_sleep(2, 3)
#                 except Exception:
#                     break  # no next button → stop loop

#             except Exception as e:
#                 print(f"[!] Error while parsing months: {e}")
#                 break

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

#     # 🔹 Step 1: Month view (multi-month loop)
#     try:
#         month_btn = driver.find_element(By.XPATH, "//li[contains(text(),'Month')]")
#         driver.execute_script("arguments[0].click();", month_btn)
#         _human_sleep(1, 2)
#         print("[+] Switched to month view")
#         slots.extend(parse_all_months())
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

# def extract_slots(driver, months_to_scan: int = 5):
#     """
#     Extract booking slots from the calendar:
#     - Always includes the current month and up to (months_to_scan - 1) future months.
#     - Falls back to 'Available' view if month slots are not found.
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

#                 # Map index → weekday (skip leftbar)
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
#             for slot in driver.find_elements(By.CSS_SELECTOR, ".achip"):
#                 parsed.append({
#                     "view": "Available",
#                     "month": None,
#                     "day": None,
#                     "weekday": None,
#                     "time": slot.text.strip(),
#                     "status": "Available"
#                 })
#         except TimeoutException:
#             print("[⚠️] No slots found in available view.")
#         return parsed

#     print("[*] Looking for booking calendar...")

#     # 🔹 Step 1: Month view (fixed months_to_scan months)
#     try:
#         driver.find_element(By.XPATH, "//li[contains(text(),'Month')]").click()
#         _human_sleep(1, 2)
#         print("[+] Switched to month view")

#         for i in range(months_to_scan):
#             # Get current month label
#             month_label = driver.find_element(By.CSS_SELECTOR, ".month .mid").text.strip()
#             print(f"[📅] Scanning {month_label} ({i+1}/{months_to_scan})")

#             slots.extend(parse_month_slots(month_label))

#             # Move to next month unless this is the last iteration
#             if i < months_to_scan - 1:
#                 try:
#                     driver.find_element(By.CSS_SELECTOR, ".navhead .i-r").click()
#                     _human_sleep(2, 3)
#                 except Exception:
#                     print("[ℹ️] No more months available.")
#                     break
#     except Exception as e:
#         print(f"[!] Could not switch to month view: {e}")

#     # 🔹 Step 2: Available view fallback
#     try:
#         driver.find_element(By.XPATH, "//li[contains(text(),'Available')]").click()
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


def extract_slots(driver, months_ahead: int = 4):
    """
    Extract booking slots from the calendar:
    - Loops through a fixed number of months (default = 5).
    - Falls back to 'Available' view if month slots are not found.
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

            # Extract weekday headers
            weekday_headers = month_container.find_elements(By.CSS_SELECTOR, "thead th")
            weekdays = [w.text.strip() for w in weekday_headers if w.text.strip()]

            # Extract day cells
            day_cells = month_container.find_elements(By.CSS_SELECTOR, "tbody td")
            for idx, cell in enumerate(day_cells):
                day_num = cell.text.strip()
                classes = cell.get_attribute("class")

                if not day_num or "other" in classes:
                    continue  # skip empty/other-month days

                # Map index → weekday (skip leftbar cells)
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

                parsed.append({
                    "view": "Month",
                    "month": month_label,
                    "day": day_num,
                    "weekday": weekday,
                    "status": status
                })

            # Save screenshot
            _save_screenshot(driver, f"calendar_{month_label.replace(' ', '_')}")

        except Exception as e:
            print(f"[!] Error parsing month {month_label}: {e}")

        return parsed

    def parse_available_view():
        parsed = []
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".achip"))
            )
            slot_divs = driver.find_elements(By.CSS_SELECTOR, ".achip")
            for slot in slot_divs:
                time_text = slot.text.strip()
                parsed.append({
                    "view": "Available",
                    "month": None,
                    "day": None,
                    "weekday": None,
                    "time": time_text,
                    "status": "Available"
                })
        except TimeoutException:
            print("[⚠️] No slots found in available view.")
        return parsed

    print("[*] Looking for booking calendar...")

    # 🔹 Step 1: Month view (loop fixed number of months)
    try:
        month_btn = driver.find_element(By.XPATH, "//li[contains(text(),'Month')]")
        driver.execute_script("arguments[0].click();", month_btn)
        _human_sleep(1, 2)
        print("[+] Switched to month view")

        for i in range(months_ahead):
            # Get current month label
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

    # 🔹 Step 2: Available view fallback
    try:
        avail_btn = driver.find_element(By.XPATH, "//li[contains(text(),'Available')]")
        driver.execute_script("arguments[0].click();", avail_btn)
        _human_sleep(1, 2)
        print("[+] Switched to available view")
        slots.extend(parse_available_view())
    except Exception as e:
        print(f"[!] Could not switch to available view: {e}")

    # Summary
    if slots:
        print_slots_grouped(slots)
    else:
        print("[⚠️] No slots extracted.")
    return slots





# ---------------- CSV Saving ----------------

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
            writer.writerow(["Extracted_At", "Month", "Date", "Weekday", "Time", "Status", "View"])

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        saved_count = 0
        for s in slots:
            weekday = (s.get("weekday") or "").upper()
            if weekday in WEEKEND_SKIP:
                continue  # skip weekends

            date_text = s.get("date") or "Unknown"
            month_label = date_text.split()[0] if " " in date_text else date_text

            writer.writerow([
                now_str,
                month_label,
                date_text,
                s.get("weekday", ""),
                s.get("time", ""),
                s.get("status", ""),
                s.get("view", ""),
            ])
            saved_count += 1

    print(f"[💾] Saved {saved_count} weekday slots → {filename}")


# ---------------- Console Printing ----------------

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

def print_slots_grouped(slots):
    """Pretty print slots grouped by month. Weekends are skipped in availability, but shown in grey."""
    if not slots:
        print("[⚠️] No slots extracted this run.")
        return

    grouped = defaultdict(list)
    for s in slots:
        # month label from date (if available)
        month_label = s["date"].split()[0] if s["date"] else "Unknown"
        grouped[month_label].append(s)

    print("\n📅 All slots (month-wise):")
    for month, month_slots in grouped.items():
        print(f"\n  {month}:")
        for s in month_slots:
            weekday = s.get("weekday", "") or ""
            if weekday.upper() in WEEKEND_SKIP:
                # Highlight weekends in grey
                print(f"    {GREY}{s['date']} ({weekday}) {s['time']} → {s['status']} [Skipped Weekend]{RESET}")
            else:
                print(f"    {s['date']} ({weekday}) {s['time']} → {s['status']}")

    print("\n🎉 Available slots (weekdays only):")
    available = [s for s in slots if s["status"] == "Available" and (s.get("weekday") or "").upper() not in WEEKEND_SKIP]
    if available:
        for s in available:
            print(f"  {s['date']} ({s.get('weekday','')}) {s['time']} → Available")
    else:
        print("  ❌ No available weekday slots right now.")

