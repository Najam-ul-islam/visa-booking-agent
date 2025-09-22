import time
import requests
from config.settings import API_KEY_2CAPTCHA, SITE_URL, SITE_KEY

def solve_turnstile():
    # Step 1: Create task
    resp = requests.post("http://2captcha.com/in.php", data={
        "key": API_KEY_2CAPTCHA,
        "method": "turnstile",
        "sitekey": SITE_KEY,
        "pageurl": SITE_URL,
        "json": 1
    }).json()

    if resp["status"] != 1:
        raise Exception(f"2Captcha error: {resp}")

    task_id = resp["request"]

    # Step 2: Poll result
    for i in range(25):
        res = requests.get("http://2captcha.com/res.php", params={
            "key": API_KEY_2CAPTCHA,
            "action": "get",
            "id": task_id,
            "json": 1
        }).json()

        if res["status"] == 1:
            return res["request"]

        time.sleep(5)

    raise TimeoutError("2Captcha solving timed out")
