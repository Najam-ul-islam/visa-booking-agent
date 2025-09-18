import undetected_chromedriver as uc
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

def init_browser(headless: bool = False, proxy: str | None = None, user_agent: str | None = None):
    """Initialize undetected Chrome driver with human-like arguments."""
    options = uc.ChromeOptions()

    # Human-like window + behavior
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--lang=en-US,en;q=0.9")
    options.add_argument("--start-maximized")
    options.add_argument("--window-size=1280,800")

    if headless:
        options.add_argument("--headless=new")

    if proxy:
        options.add_argument(f'--proxy-server={proxy}')

    if user_agent:
        options.add_argument(f'--user-agent={user_agent}')
    else:
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
        options.add_argument(f"--user-agent={ua}")

    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "intl.accept_languages": "en,en-US"
    }
    options.add_experimental_option("prefs", prefs)

    caps = DesiredCapabilities.CHROME.copy()
    caps["goog:loggingPrefs"] = {"performance": "ALL", "browser": "ALL"}  # type: ignore

    driver = uc.Chrome(options=options, desired_capabilities=caps)
    driver.implicitly_wait(5)
    return driver



# # booking/browser.py
# # Creates an undetected Chrome browser instance with human-like settings.

# import undetected_chromedriver as uc
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# def init_browser(headless: bool = False, proxy: str | None = None, user_agent: str | None = None):
#     """
#     Initialize undetected Chrome driver with human-like arguments.
#     - headless: set False for visible mode (recommended during debugging and manual solves).
#     - proxy: optional proxy string like "http://user:pass@host:port" or "socks5://host:port".
#     - user_agent: custom UA string (otherwise default modern Chrome UA will be used).
#     """

#     options = uc.ChromeOptions()

#     # Human-like window + behavior
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--disable-infobars")
#     options.add_argument("--disable-extensions")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--lang=en-US,en;q=0.9")
#     options.add_argument("--start-maximized")
#     options.add_argument("--window-size=1280,800")

#     # Headless toggle - undetected chromedriver supports headless
#     if headless:
#         # prefer the new headless mode
#         options.add_argument("--headless=new")

#     # Optional proxy
#     if proxy:
#         options.add_argument(f'--proxy-server={proxy}')

#     # Custom user agent if provided (or preserve undetected default)
#     if user_agent:
#         options.add_argument(f'--user-agent={user_agent}')
#     else:
#         # A modern Chrome UA (keeps undetected defaults if you prefer)
#         ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
#         options.add_argument(f"--user-agent={ua}")

#     # Experimental options to remove webdriver flag in navigator
#     prefs = {
#         "credentials_enable_service": False,
#         "profile.password_manager_enabled": False,
#         "intl.accept_languages": "en,en-US"
#     }
#     options.add_experimental_option("prefs", prefs)

#     # Capabilities: enable performance logging if needed
#     caps = DesiredCapabilities.CHROME.copy()
#     # type: ignore is used to suppress type checker complaints about dict assignment
#     caps["goog:loggingPrefs"] = {"performance": "ALL", "browser": "ALL"}  # type: ignore

#     driver = uc.Chrome(options=options, desired_capabilities=caps)
#     # set an implicit wait for convenience (use explicit waits wherever possible)
#     driver.implicitly_wait(5)
#     return driver
