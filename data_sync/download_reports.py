import os
import time
from datetime import datetime, timedelta

import pyotp
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.firefox import GeckoDriverManager

from utils.logger import get_logger
from utils.config_loader import Env, sc
from utils.date_time_utils import today_indian

logger = get_logger(__name__)  # Initialize logger

# 🔹 Constants
START_DATE = datetime(2017, 1, 1).date()
END_DATE = today_indian()

# 🔹 Flags for enabling/disabling downloads
DOWNLOAD_FLAGS = {
    "Tradebook": True,
    "P&L": True,
    "Ledger": True,
    "Tax Reports": True,
    "Holdings": True,
    "Positions": True,
}

# 🔹 Zerodha Console Report URLs
REPORT_LINKS = {
    "Tradebook": "https://console.zerodha.com/reports/tradebook",
    "P&L": "https://console.zerodha.com/reports/pnl",
    "Ledger": "https://console.zerodha.com/reports/ledger",
    "Tax Reports": "https://console.zerodha.com/reports/tax",
    "Holdings": "https://console.zerodha.com/portfolio/holdings",
    "Positions": "https://console.zerodha.com/portfolio/positions",
}

FAILED_REPORTS = []  # Track failed downloads


def generate_totp():
    """Generate a valid TOTP using the secret key."""
    return pyotp.TOTP(Env.TOTP_TOKEN).now()


def setup_driver():
    """Setup Firefox WebDriver with auto-download settings."""
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    # ✅ Set Download Preferences
    download_path = os.path.abspath(Env.DOWNLOAD_DIR)
    print(download_path)
    options.set_preference("browser.download.folderList", 2)  # Use custom directory
    options.set_preference("browser.download.dir", download_path)  # Ensure absolute path
    options.set_preference("browser.download.useDownloadDir", True)
    options.set_preference("browser.download.panel.shown", False)  # Hide download panel
    options.set_preference("browser.helperApps.neverAsk.saveToDisk",
                           "text/csv,application/csv,application/vnd.ms-excel")  # Auto-download CSVs

    # ✅ Disable Built-in PDF Viewer (Prevents Download Errors)
    options.set_preference("pdfjs.disabled", True)

    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)
    return driver



def highlight_element(driver, element):
    """Highlight a Selenium WebElement for debugging."""
    driver.execute_script("arguments[0].style.border='3px solid red'", element)
    time.sleep(0.5)


def login_kite(driver):
    """Automates Zerodha Kite login using Selenium (Firefox)."""
    logger.info("🔹 Logging into Zerodha Kite...")
    print("🔹 Opening Zerodha Kite login page...")

    driver.get("https://kite.zerodha.com/")
    time.sleep(2)

    try:
        userid_field = driver.find_element(By.ID, "userid")
        highlight_element(driver, userid_field)
        userid_field.send_keys(Env.ZERODHA_USERNAME)
        print("✅ Entered User ID.")

        password_field = driver.find_element(By.ID, "password")
        highlight_element(driver, password_field)
        password_field.send_keys(Env.ZERODHA_PASSWORD)
        print("✅ Entered Password.")

        login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
        highlight_element(driver, login_button)
        login_button.click()
        print("🔹 Submitted login credentials.")

        # Wait for TOTP field
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@type='number']")))
        totp_field = driver.find_element(By.XPATH, "//input[@type='number']")
        highlight_element(driver, totp_field)

        ztotp = generate_totp()
        print(f"🔹 Generated TOTP: {ztotp}")
        totp_field.send_keys(ztotp)
        time.sleep(2)

        for attempt in range(sc.MAX_TOTP_CONN_RETRY_COUNT):
            if "dashboard" in driver.current_url:
                print("✅ Login Successful!")
                logger.info("✅ Login Successful!")
                return
            else:
                print("⚠️ Invalid TOTP! Retrying...")
                logger.warning("⚠️ Invalid TOTP! Retrying...")
                time.sleep(2)

    except Exception as e:
        logger.error(f"❌ Login Failed: {e}")
        print(f"❌ Login Failed: {e}")
        driver.quit()
        raise


import pandas as pd
from selenium.webdriver.support.ui import Select


def download_reports(driver):
    """Downloads reports from Zerodha Console."""
    os.makedirs(Env.DOWNLOAD_DIR, exist_ok=True)

    try:
        for name, url in REPORT_LINKS.items():
            if not DOWNLOAD_FLAGS.get(name, False):
                continue

            logger.info(f"📂 Downloading: {name}")
            print(f"📂 Downloading: {name}")

            driver.get(url)
            time.sleep(5)

            current_start = START_DATE
            while current_start < END_DATE:
                current_end = min(current_start + timedelta(days=364), END_DATE)

                try:
                    dropdown = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//select'))
                    )
                    highlight_element(driver, dropdown)
                    select = Select(dropdown)
                    select.select_by_visible_text("Equity")
                    print("✅ Selected Equity in dropdown.")
                except Exception as e:
                    print(f"❌ Dropdown selection failed: {e}")

                try:
                    start_date_input = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="Select range"]'))
                    )
                    highlight_element(driver, start_date_input)
                    time.sleep(2)

                    values = start_date_input.get_attribute("value")
                    values = f'{current_start.strftime("%Y-%m-%d")}{values[10:13]}{current_end.strftime("%Y-%m-%d")}'

                    start_date_input.send_keys(Keys.CONTROL + "a")
                    start_date_input.clear()
                    start_date_input.send_keys(Keys.BACKSPACE)
                    start_date_input.send_keys(values)
                    print(f"✅ Set Date Range: {values}")

                    apply_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
                    )
                    highlight_element(driver, apply_button)
                    apply_button.click()
                    print("✅ Applied Date Filter.")

                except Exception as e:
                    print(f"❌ Failed to set date range: {e}")

                try:
                    download_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "CSV")]'))
                    )
                    highlight_element(driver, download_button)
                    download_button.click()
                    print("✅ Downloading Report.")
                except Exception as e:
                    print(f"❌ Failed to download report: {e}")
                    FAILED_REPORTS.append(name)

                current_start = current_end + timedelta(days=1)

    except Exception as e:
        logger.error(f"❌ Error while downloading reports: {e}")
        print(f"❌ Error while downloading reports: {e}")

    finally:
        driver.quit()
        print("\n🔹 All tasks completed!\n")
        logger.info("\n🔹 All tasks completed!\n")

        if FAILED_REPORTS:
            print("⚠️ Some reports failed to download:")
            for report in FAILED_REPORTS:
                print(f"  ❌ {report}")
        else:
            print("✅ All reports downloaded successfully!")


def main():
    """Main function to test login and report downloads."""
    test_login_only = False

    driver = setup_driver()
    try:
        login_kite(driver)
        if not test_login_only:
            print("✅ Login successful! Proceeding with downloads...")
            download_reports(driver)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()

