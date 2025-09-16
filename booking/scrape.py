import time
from selenium.webdriver.common.by import By
from config.settings import SITE_URL

def scrape_slots(driver):
    if not SITE_URL:
        raise ValueError("SITE_URL is not set or is None.")
    driver.get(SITE_URL + "schedule/grcon-isl-pakistan/National_visa_for_WORK")
    time.sleep(5)

    slots = []
    for el in driver.find_elements(By.CSS_SELECTOR, ".slot"):
        slots.append({"id": el.get_attribute("data-slot-id"), "text": el.text})

    return slots
