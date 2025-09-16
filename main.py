# from booking.browser import init_browser
# from captcha.solver import solve_turnstile
# from booking.login import login
# from booking.scrape import scrape_slots
# from booking.book import book_slot
# from agents.slot_selector import choose_best_slot

# def main():
#     driver = init_browser(headless=False)

#     try:
#         # Step 1: Solve captcha
#         token = solve_turnstile()
#         print("Turnstile token:", token)

#         # Step 2: Login
#         login(driver, token)

#         # Step 3: Scrape slots
#         slots = scrape_slots(driver)
#         print("Slots found:", slots)

#         if not slots:
#             print("No slots available.")
#             return

#         # Step 4: AI selects slot
#         choice = choose_best_slot(slots)
#         print("AI picked:", choice)

#         # Step 5: Book slot
#         confirmation = book_slot(driver, slots[0]["id"], {"name": "John Doe", "passport": "AB123456"})
#         print("Booking confirmation page:", confirmation[:500])

#     finally:
#         driver.quit()

# if __name__ == "__main__":
#     main()


# from booking.browser import init_browser
# from booking.login import login
# from booking.scrape import scrape_slots
# from booking.book import book_slot
# from agents.slot_selector import choose_best_slot

# def main():
#     driver = init_browser(headless=False)

#     try:
#         # Step 1: Go to homepage (let Turnstile auto-verify)
#         driver.get("https://schedule.cf-grcon-isl-pakistan.com/")
#         print("Waiting for Turnstile check...")
#         driver.implicitly_wait(10)  # Let it auto-pass

#         # Step 2: Login directly (no 2Captcha)
#         login(driver)

#         # Step 3: Scrape slots
#         slots = scrape_slots(driver)
#         print("Slots found:", slots)

#         if not slots:
#             print("No slots available.")
#             return

#         # Step 4: Decision making
#         choice = choose_best_slot(slots)
#         print("Gemini picked:", choice)

#         # Step 5: Book slot
#         confirmation = book_slot(driver, slots[0]["id"], {"name": "John Doe", "passport": "AB123456"})
#         print("Booking confirmation page:", confirmation[:500])

#     finally:
#         driver.quit()

# if __name__ == "__main__":
#     main()




from booking.browser import init_browser
from booking.login import login
from config.settings import USERNAME, PASSWORD

if USERNAME is None or PASSWORD is None:
    raise ValueError("USERNAME and PASSWORD must not be None.")

driver = init_browser(headless=False, proxy=None)  # headless=False 
try:
    login(driver, headless=False)
    
    print("Logged in Successfully!!!!!!!!!!")
    # continue with scrape/book flow...
finally:
    driver.quit()
