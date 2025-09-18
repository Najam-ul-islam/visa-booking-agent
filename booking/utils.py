import os
import time
import random
import re
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


from config.settings import SAVE_SCREENSHOTS

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
