import os
import time
from datetime import datetime, timedelta

import pyotp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from utils.logger import get_logger
from utils.config_loader import Env, sc
from utils.date_time_utils import today_indian
from selenium.webdriver.common.keys import Keys

logger = get_logger(__name__)  # Initialize logger

# 🔹 Set the start date for reports (default: last 10 years)
START_DATE = datetime(2017,1,1).date()
END_DATE = today_indian()

# 🔹 Flags to enable/disable report downloads
DOWNLOAD_FLAGS = {
    "Tradebook": True,
    "P&L": True,
    "Ledger": True,
    "Tax Reports": True,
    "Holdings": True,
    "Positions": True,
}

# 🔹 Report Links (from Zerodha Console)
REPORT_LINKS = {
    "Tradebook": "https://console.zerodha.com/reports/tradebook",
    "P&L": "https://console.zerodha.com/reports/pnl",
    "Ledger": "https://console.zerodha.com/reports/ledger",
    "Tax Reports": "https://console.zerodha.com/reports/tax",
    "Holdings": "https://console.zerodha.com/portfolio/holdings",
    "Positions": "https://console.zerodha.com/portfolio/positions",
}

# 🔹 Track failed reports
FAILED_REPORTS = []


def generate_totp():
    """Generate a valid TOTP using the secret key."""
    return pyotp.TOTP(Env.TOTP_TOKEN).now()


def setup_driver():
    """Setup Chrome WebDriver with download settings."""
    options = Options()
    # 🔹 REMOVE HEADLESS MODE FOR DEBUGGING
    # options.add_argument("--headless")  # Comment this line out to see the browser
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    # Configure Chrome to auto-download files
    prefs = {
        "download.default_directory": Env.DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "safebrowsing.disable_download_protection": True,
    }
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver
print(Env.DOWNLOAD_DIR)

def highlight_element(driver, element):
    """Highlight a Selenium WebElement for debugging."""
    driver.execute_script("arguments[0].style.border='3px solid red'", element)
    time.sleep(0.5)  # Briefly highlight the element


def login_kite(driver):
    """Automates Zerodha Kite login using Selenium."""
    logger.info("🔹 Logging into Zerodha Kite...")
    print("🔹 Opening Zerodha Kite login page...")

    driver.get("https://kite.zerodha.com/")
    time.sleep(2)  # Wait for page to load

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
        print("🔹 Submitted TOTP.")
        time.sleep(2)
        # Wait for TOTP input field
        for attempt in range(sc.MAX_TOTP_CONN_RETRY_COUNT):
            if "dashboard" in driver.current_url:
                print("✅ Login Successful!")
                logger.info("✅ Login Successful!")
                return  # Exit function if login is successful
            else:
                print("⚠️ Invalid TOTP detected! Retrying...")
                logger.warning("⚠️ Invalid TOTP detected! Retrying...")
                time.sleep(2)  # Small delay before retrying

    except Exception as e:
        logger.error(f"❌ Login Failed: {e}")
        print(f"❌ Login Failed: {e}")
        driver.quit()
        raise


import os
import pandas as pd
from datetime import timedelta
from selenium.webdriver.support.ui import Select


def merge_csv_files(report_name, category):
    """Merges all downloaded CSVs for a given category into a single file."""
    download_dir = Env.DOWNLOAD_DIR
    merged_filename = os.path.join(download_dir, f"{report_name}_{category}_merged.csv")
    all_files = [os.path.join(download_dir, f) for f in os.listdir(download_dir) if
                 f.startswith(f"{report_name}_{category}_") and f.endswith(".csv")]

    if not all_files:
        print(f"⚠️ No files found for {report_name} ({category}) to merge.")
        return

    combined_df = pd.concat([pd.read_csv(f) for f in all_files], ignore_index=True)
    combined_df.to_csv(merged_filename, index=False)
    print(f"✅ Merged {len(all_files)} files into {merged_filename}")


def download_reports(driver):
    """Downloads reports from Zerodha Console, handles date ranges, and merges CSVs."""
    os.makedirs(Env.DOWNLOAD_DIR, exist_ok=True)

    try:
        for name, url in REPORT_LINKS.items():
            if DOWNLOAD_FLAGS.get(name, False):  # Check if report download is enabled
                logger.info(f"📂 Downloading: {name}")
                print(f"📂 Downloading: {name}")

                driver.get(url)
                time.sleep(5)  # Wait for page to load

                # Set date range (one year at a time)
                current_start = START_DATE
                while current_start < END_DATE:
                    current_end = min(current_start + timedelta(days=364), END_DATE)

                    # Select start date
                    # ✅ Open Tradebook Page
                    driver.get("https://console.zerodha.com/reports/tradebook")
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

                    # ✅ **Step 1: Select Dropdown ("Equity" or "Futures & Options")**
                    try:
                        dropdown = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, '//select'))
                            # Replace with actual class
                        )
                        highlight_element(driver, dropdown)  # 🔹 Highlight dropdown
                        select = Select(dropdown)
                        select.select_by_visible_text("Equity")  # Change to "Futures & Options" if needed
                        print("✅ Selected Equity in dropdown.")
                    except Exception as e:
                        print(f"❌ Failed to select dropdown item: {e}")

                    # ✅ **Step 2: Set Date Range (1 Year at a Time)**
                    try:
                        start_date = (datetime.today() - timedelta(days=365)).strftime("%Y-%m-%d")  # 1 year ago
                        end_date = datetime.today().strftime("%Y-%m-%d")  # Today's date

                        start_date_input = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="Select range"]'))
                            # Modify if needed
                        )
                        highlight_element(driver, start_date_input)  # 🔹 Highlight start date input
                        # start_date_input.clear()
                        time.sleep(2)

                        values = start_date_input.get_attribute("value")
                        print(values)

                        values = f'{start_date}{values[10:13]}{end_date}'
                        print(f"✅ Set Start Date: {values}")
                        start_date_input.send_keys(Keys.CONTROL + "a")  # Select all (Windows/Linux)
                        start_date_input.clear()
                        start_date_input.send_keys(Keys.BACKSPACE)  # Clear existing text
                        start_date_input.send_keys(values)
                        print(f"✅ Set Start Date: {values}")


                        # Click Apply Button
                        apply_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
                        )
                        highlight_element(driver, apply_button)  # 🔹 Highlight apply button
                        apply_button.click()
                        print("✅ Applied Date Filter.")

                    except Exception as e:
                        print(f"❌ Failed to set date range: {e}")

                    # ✅ **Step 3: Download Tradebook**
                    try:
                        download_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "CSV")]'))
                        )
                        highlight_element(driver, download_button)  # 🔹 Highlight download button
                        download_button.click()
                        print("✅ Downloading Tradebook.")
                    except Exception as e:
                        print(f"❌ Failed to download tradebook: {e}")

                    # Move to the next year
                    current_start = current_end + timedelta(days=1)

                # Merge files after downloading for both categories
                merge_csv_files(name, "Equity")
                merge_csv_files(name, "Futures & Options")

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
    test_login_only = False  # Set True to only test login

    driver = setup_driver()
    try:
        login_kite(driver)

        if not test_login_only:
            logger.info("✅ Login successful! Proceeding with downloads...")
            print("✅ Login successful! Proceeding with downloads...")
            download_reports(driver)
        else:
            logger.info("✅ Login successful! Skipping report downloads for test mode.")
            print("✅ Login successful! Skipping report downloads for test mode.")

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        print(f"❌ Error: {e}")

    finally:
        driver.quit()
        print("🔹 Test completed!")
        logger.info("🔹 Test completed!")


# Run script
if __name__ == "__main__":
    main()
