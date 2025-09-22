import time
from selenium.webdriver.common.by import By

def book_slot(driver, slot_id, applicant):
    button = driver.find_element(By.XPATH, f"//button[@data-slot-id='{slot_id}']")
    button.click()
    time.sleep(2)

    # Example form-filling
    driver.find_element(By.NAME, "name").send_keys(applicant["name"])
    driver.find_element(By.NAME, "passport").send_keys(applicant["passport"])
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    time.sleep(5)
    return driver.page_source  # confirmation HTML
