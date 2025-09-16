# from datetime import datetime
# import os
# import time
# import random
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException
# from config.settings import PASSWORD, USERNAME


# def _human_sleep(min_s=0.4, max_s=1.2):
#     time.sleep(random.uniform(min_s, max_s))


# def save_debug(driver, step_name: str):
#     """Save screenshot + HTML dump into ./screenshots with timestamped filenames."""
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


# def login(driver, username: str=USERNAME, password: str=PASSWORD, headless=False, max_retries=3):
#     root = "https://schedule.cf-grcon-isl-pakistan.com/"
#     print("[*] Opening homepage:", root)
#     driver.get(root)
#     save_debug(driver, "step_1_home")

#     # ---- Handle Turnstile ----
#     print("[*] Waiting for Turnstile or redirect...")
#     try:
#         WebDriverWait(driver, 20).until(
#             lambda d: "/landing/home" in d.current_url
#                       or len(d.find_elements(By.TAG_NAME, "iframe")) > 0
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
#                               or "National visa for WORK" in d.page_source
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

#     # ---- Login Form ----
#     print("[*] Waiting for login page to load...")
#     import random

#     # ---- Retry loop for login ----
#     for attempt in range(1, max_retries + 1):
#         print(f"[*] Attempt {attempt}/{max_retries} to log in...")

#         try:
#             email_box = WebDriverWait(driver, 20).until(
#                 EC.presence_of_element_located((By.NAME, "name"))
#             )
#             password_box = WebDriverWait(driver, 20).until(
#                 EC.presence_of_element_located((By.NAME, "password"))
#             )
#             print("[+] Found login form fields")

#             # Fill form
#             email_box.clear()
#             email_box.send_keys(username)
#             _human_sleep()
#             password_box.clear()
#             password_box.send_keys(password)
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
#                 save_debug(driver, f"step_6_login_failed_attempt{attempt}")
#                 print(f"[❌] Login failed on attempt {attempt}.")

#                 if attempt < max_retries:
#                     base_backoff = 5 * (2 ** (attempt - 1))  # 5, 10, 20
#                     jitter = random.uniform(1.0, 1.3)        # +0–30%
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

#     # try:
#     #     email_box = WebDriverWait(driver, 20).until(
#     #         EC.presence_of_element_located((By.NAME, "name"))
#     #     )
#     #     password_box = WebDriverWait(driver, 20).until(
#     #         EC.presence_of_element_located((By.NAME, "password"))
#     #     )
#     #     print("[+] Found login form fields")
#     # except TimeoutException:
#     #     save_debug(driver, "step_4_login_failed")
#     #     raise RuntimeError("❌ Could not find login form.")

#     # # Fill form
#     # email_box.clear()
#     # email_box.send_keys(username)
#     # _human_sleep()
#     # password_box.clear()
#     # password_box.send_keys(password)
#     # _human_sleep()
#     # save_debug(driver, "step_5_filled_login")

#     # # Submit
#     # try:
#     #     submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
#     #     submit_btn.click()
#     #     print("[+] Clicked submit button")
#     # except Exception:
#     #     print("[!] Could not find submit button. Pressing Enter on password field.")
#     #     password_box.send_keys("\n")

#     # # ---- Post-login Validation ----
#     # try:
#     #     WebDriverWait(driver, 30).until(
#     #         EC.any_of(
#     #             EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'Log out')]")),
#     #             EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Available slots')]")),
#     #         )
#     #     )
#     #     save_debug(driver, "step_6_login_success")
#     #     print("[✅] Login successful! Slots page is accessible.")
#     #     return True
#     # except TimeoutException:
#     #     save_debug(driver, "step_6_login_failed")
#     #     print("[❌] Login failed or slots page not found.")
#     #     return False







import os
import time
import random
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config import settings


def _human_sleep(min_s=0.4, max_s=1.2):
    """Sleep randomly to simulate human typing delays."""
    time.sleep(random.uniform(min_s, max_s))


def save_debug(driver, step_name: str):
    """Save screenshot + HTML dump if SAVE_DEBUG=True."""
    if not settings.SAVE_DEBUG:
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


def login(driver, headless=False, max_retries: int = 3):
    root = settings.SITE_URL
    print("[*] Opening homepage:", root)
    driver.get(root)
    save_debug(driver, "step_1_home")

    # ---- Handle Turnstile ----
    print("[*] Waiting for Turnstile or redirect...")
    try:
        WebDriverWait(driver, 20).until(
            lambda d: "/landing/home" in d.current_url
            or len(d.find_elements(By.TAG_NAME, "iframe")) > 0
        )
    except Exception:
        pass
    save_debug(driver, "step_2_turnstile")

    if "/landing/home" in driver.current_url:
        print("[+] Already passed Turnstile -> on landing/home ✅")
    else:
        print("[!] Could not auto-pass Turnstile. Solve manually if visible.")
        if headless:
            raise RuntimeError("Headless=True but manual Turnstile solve required. Use headless=False.")
        else:
            print("[*] Waiting up to 2 minutes for manual Turnstile solve...")
            try:
                WebDriverWait(driver, 120).until(
                    lambda d: "/landing/home" in d.current_url
                    or "National visa for WORK" in d.page_source
                )
                print("[+] Turnstile solved manually → category page loaded ✅")
            except Exception:
                raise RuntimeError("Turnstile not solved in time.")
    save_debug(driver, "step_3_category")

    # ---- Category Page ----
    print("[*] Waiting for category options...")
    try:
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
            print("[+] Clicked link using ActionChains")
        _human_sleep(2, 3)
    except Exception as e:
        raise RuntimeError(f"❌ Could not click 'National visa for WORK': {e}")
    save_debug(driver, "step_4_after_work_click")

    # ---- Retry loop for login ----
    for attempt in range(1, max_retries + 1):
        print(f"[*] Attempt {attempt}/{max_retries} to log in...")

        try:
            email_box = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "name"))
            )
            # email_box = WebDriverWait(driver, 20).until(
            #     EC.element_to_be_clickable((By.ID, "email")))
            password_box = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            print("[+] Found login form fields")

            # Fill form
            email_box.clear()
            email_box.send_keys(settings.USERNAME)
            _human_sleep()
            password_box.clear()
            password_box.send_keys(settings.PASSWORD)
            _human_sleep()
            save_debug(driver, f"step_5_filled_login_attempt{attempt}")

            # Submit
            try:
                submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                submit_btn.click()
                print("[+] Clicked submit button")
            except Exception:
                print("[!] Could not find submit button. Pressing Enter on password field.")
                password_box.send_keys("\n")

            # ---- Post-login Validation ----
            try:
                WebDriverWait(driver, 60).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'Log out')]")),
                        EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Available slots')]")),
                        EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Welcome')]")),
                        EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Dashboard')]")),
                        EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Booking')]")),
                    )
                )
                save_debug(driver, f"step_6_login_success_attempt{attempt}")
                print("[✅] Login successful!")
                return True
            except TimeoutException:
                # Detect error banners
                error_text = ""
                try:
                    err = driver.find_element(By.CSS_SELECTOR, ".alert-danger, .error, .login-error")
                    error_text = err.text.strip()
                except NoSuchElementException:
                    if "invalid login" in driver.page_source.lower():
                        error_text = "Invalid login name or password (found in page)"
                save_debug(driver, f"step_6_login_failed_attempt{attempt}")
                print(f"[❌] Login failed on attempt {attempt}. Server message: {error_text}")

                if attempt < max_retries:
                    base_backoff = 5 * (2 ** (attempt - 1))  # 5, 10, 20
                    jitter = random.uniform(1.0, 1.3)        # add +0–30%
                    wait_time = int(base_backoff * jitter)
                    print(f"[*] Retrying after ~{wait_time} seconds...")
                    driver.refresh()
                    time.sleep(wait_time)
                    continue
                else:
                    return False

        except TimeoutException:
            save_debug(driver, f"step_5_login_form_not_found_attempt{attempt}")
            print(f"[❌] Login form not found on attempt {attempt}.")
            if attempt < max_retries:
                base_backoff = 5 * (2 ** (attempt - 1))
                jitter = random.uniform(1.0, 1.3)
                wait_time = int(base_backoff * jitter)
                print(f"[*] Retrying after ~{wait_time} seconds...")
                driver.refresh()
                time.sleep(wait_time)
                continue
            else:
                return False
