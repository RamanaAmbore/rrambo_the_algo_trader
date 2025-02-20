from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from dotenv import load_dotenv
from utils.logger import get_logger
from auth.totp import generate_totp

# Load environment variables
load_dotenv()

logger = get_logger(__name__)


def zerodha_login():
    """Logs into Zerodha Kite and fetches the access token."""
    username = os.getenv("ZERODHA_USERNAME")
    password = os.getenv("ZERODHA_PASSWORD")
    kite_login_url = "https://kite.zerodha.com/"

    if not username or not password:
        raise ValueError("Zerodha username or password is missing in .env")

    logger.info("Launching browser for Zerodha login...")

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(kite_login_url)
        time.sleep(2)  # Allow page to load

        logger.info("Entering username and password...")
        driver.find_element(By.ID, "userid").send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(2)

        # Generate and enter TOTP
        logger.info("Generating TOTP...")
        totp_code = generate_totp()
        driver.find_element(By.ID, "totp").send_keys(totp_code)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(3)

        # Fetch request token from URL
        logger.info("Fetching request token from redirected URL...")
        current_url = driver.current_url
        if "request_token=" in current_url:
            request_token = current_url.split("request_token=")[1].split("&")[0]
            logger.info("Request token retrieved successfully.")
        else:
            raise Exception("Failed to retrieve request token")

    finally:
        driver.quit()

    return request_token


if __name__ == "__main__":
    print("Request Token:", zerodha_login())
