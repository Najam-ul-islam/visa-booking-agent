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




# from booking.browser import init_browser
# from booking.login import login
# from config.settings import EMAIL, PASSWORD

# if EMAIL is None or PASSWORD is None:
#     raise ValueError("USERNAME and PASSWORD must not be None.")

# driver = init_browser(headless=False, proxy=None)  # headless=False 
# try:
#     login(driver, headless=False)
    
#     # continue with scrape/book flow...
# finally:
#     driver.quit()

# from booking.browser import init_browser
# from booking.login import login, extract_slots

# def main():
#     # ---- Create browser ----
#     driver = init_browser(headless=False)  # set True if you want headless automation
#     try:
#         # ---- Run login flow ----
#         if login(driver):
#             print("[✅] Logged in successfully!")

#             # ---- Extract slots ----
#             slots = extract_slots(driver)
#             if slots:
#                 print(f"[🎉] Found {len(slots)} slot(s):")
#                 for s in slots:
#                     print("   ", s)
#             else:
#                 print("[⚠️] No slots found.")
#         else:
#             print("[❌] Login failed.")

#         # ---- Optional pause for debugging ----
#         input("Press Enter to close browser...")

#     finally:
#         print("[*] Closing browser gracefully...")
#         driver.quit()


# if __name__ == "__main__":
#     main()

# from booking.browser import init_browser
# from booking.login import login
# from booking.slots import extract_slots, save_slots_to_csv

# def main():
#     driver = init_browser(headless=False)
#     try:
#         if login(driver):
#             slots = extract_slots(driver)
#             if slots:
#                 print("\n📅 All slots (month-wise):")
#                 for s in slots:
#                     print(f"  {s}")
#                 available = [s for s in slots if s["status"] == "Available"]
#                 print("\n🎉 Available slots:")
#                 if available:
#                     for s in available:
#                         print(f"  {s}")
#                 else:
#                     print("  ❌ No available slots right now.")
#                 save_slots_to_csv(slots)
#         else:
#             print("[❌] Could not log in. Aborting.")
#     finally:
#         input("Press Enter to close browser...")  # keep browser open
#         driver.quit()

# if __name__ == "__main__":
#     main()


from booking.browser import init_browser
from booking.login import login
from booking.slots import save_slots_to_csv

def main():
    # Start browser (headless=False so you can see & solve Turnstile)
    driver = init_browser(headless=False)

    try:
        # Run login flow
        if login(driver):
            # Extract slots after successful login
            from booking.slots import extract_slots
            slots = extract_slots(driver)

            if slots:
                print(f"\n📅 All slots found: {len(slots)}")
                for s in slots:
                    print("  ", s)

                # Save into CSV
                save_slots_to_csv(slots)
            else:
                print("\n⚠️ No slots extracted this run.")
        else:
            print("\n❌ Login failed. No slots extracted.")

    finally:
        # Keep browser open after run (optional)
        input("\nPress Enter to close browser...")
        driver.quit()


if __name__ == "__main__":
    main()
