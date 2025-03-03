import os
import time
from datetime import timedelta, datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

from utils.config_loader import Env, sc
from utils.date_time_utils import today_indian
from utils.logger import get_logger
from utils.utils import generate_totp

logger = get_logger(__name__)  # Initialize logger

# 🔹 Constants

REPORT_START_DATE = Env.REPORT_START_DATE
if REPORT_START_DATE is None:
    REPORT_START_DATE = today_indian() - timedelta(Env.REPORT_LOOKBACK_DAYS)
else:
    REPORT_START_DATE = datetime(int(REPORT_START_DATE[:4]), int(REPORT_START_DATE[5:7]),
                                 int(REPORT_START_DATE[9:])).date()

REPORT_END_DATE = today_indian()

# 🔹 Flags for enabling/disabling downloads
DOWNLOAD_FLAGS = {"Tradebook": Env.DOWNLOAD_TRADEBBOOK, "P&L": Env.DOWNLOAD_PL, "Ledger": Env.DOWNLOAD_LEDGER,
                  "Holdings": Env.DOWNLOAD_HOLDINGS, "Positions": Env.DOWNLOAD_POSITIONS, }

logger.info(f'Report start date: {REPORT_START_DATE}')
logger.info(f'Report end date: {REPORT_END_DATE}')
logger.info(f'Report list: {DOWNLOAD_FLAGS}')

FAILED_REPORTS = []  # Track failed downloads


def setup_driver():
    """Setup Firefox WebDriver with auto-download settings."""
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    # Set Download Preferences
    download_path = os.path.abspath(Env.DOWNLOAD_DIR)
    logger.info(f"Download path: {download_path}")
    options.set_preference("browser.download.folderList", 2)  # Use custom directory
    options.set_preference("browser.download.dir", download_path)  # Ensure absolute path
    options.set_preference("browser.download.useDownloadDir", True)
    options.set_preference("browser.download.panel.shown", False)  # Hide download panel
    options.set_preference("browser.helperApps.neverAsk.saveToDisk",
                           "text/csv,application/csv,application/vnd.ms-excel")  # Auto-download CSVs

    # Disable Built-in PDF Viewer (Prevents Download Errors)
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

    driver.get("https://kite.zerodha.com/")
    time.sleep(2)

    try:
        userid_field = driver.find_element(By.ID, "userid")
        highlight_element(driver, userid_field)
        userid_field.send_keys(Env.ZERODHA_USERNAME)
        logger.info("Entered User ID.")

        password_field = driver.find_element(By.ID, "password")
        highlight_element(driver, password_field)
        password_field.send_keys(Env.ZERODHA_PASSWORD)
        logger.info("Entered Password.")

        login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
        highlight_element(driver, login_button)
        login_button.click()
        logger.info("Submitted login credentials.")

        # Wait for TOTP field
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@type='number']")))
        totp_field = driver.find_element(By.XPATH, "//input[@type='number']")
        highlight_element(driver, totp_field)

        ztotp = generate_totp()
        logger.info(f"🔹 Generated TOTP: {ztotp}")
        totp_field.send_keys(ztotp)
        time.sleep(2)

        for attempt in range(sc.MAX_TOTP_CONN_RETRY_COUNT):
            if "dashboard" in driver.current_url:
                logger.info("Login Successful!")
                return
            else:
                logger.warning("Invalid TOTP! Retrying...")
                time.sleep(2)

    except Exception as e:
        logger.error(f"Login Failed: {e}")
        driver.quit()
        raise


def download_reports(driver):
    """Downloads reports from Zerodha Console."""
    os.makedirs(Env.DOWNLOAD_DIR, exist_ok=True)
    all_downloaded_files = {}
    try:
        for name, url in sc.REPORT_LINKS.items():
            if not DOWNLOAD_FLAGS.get(name, False):
                continue

            logger.info(f"Downloading: {name}")
            driver.get(url)
            time.sleep(5)
            downloaded_files = {"Equity":"", "Futures & Options":""}
            current_start = REPORT_START_DATE
            while current_start < REPORT_END_DATE:
                current_end = min(current_start + timedelta(days=364), REPORT_END_DATE)

                for segment in ["Equity", "Futures & Options"]:  # Select both segments
                    try:
                        dropdown = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, '//select')))
                        highlight_element(driver, dropdown)
                        select = Select(dropdown)
                        select.select_by_visible_text(segment)
                        logger.info(f"Selected {segment} in dropdown.")
                    except Exception as e:
                        logger.error(f"Dropdown selection failed for {segment}: {e}")
                        continue  # Skip to the next segment if selection fails

                    date_range_str = ""
                    try:
                        date_range = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="Select range"]')))
                        highlight_element(driver, date_range)
                        time.sleep(2)

                        date_range_str = date_range.get_attribute("value")
                        date_range_str = f'{current_start.strftime("%Y-%m-%d")}{date_range_str[10:13]}{current_end.strftime("%Y-%m-%d")}'

                        date_range.send_keys(Keys.CONTROL + "a")

                        date_range.send_keys(Keys.BACKSPACE)
                        date_range.clear()
                        date_range.send_keys(date_range_str)

                        arrow_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
                        highlight_element(driver, arrow_button)
                        arrow_button.click()
                        logger.info(f"Applied date filter {date_range_str} for {segment}")

                    except Exception as e:
                        logger.error(f"Failed to set date range: {date_range_str} for {segment}: {e}")
                        continue  # Skip to the next segment if date range setting fails

                    try:
                        download_csv_link = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "CSV")]')))
                        highlight_element(driver, download_csv_link)
                        files_in_dir = set(os.listdir(Env.DOWNLOAD_DIR))
                        download_csv_link.click()

                        # Wait for the file to appear in the download directory
                        downloaded_file= wait_for_download(files_in_dir)
                        downloaded_files[segment]= downloaded_files[segment] + downloaded_file
                        logger.info(f"Download completed for {segment} for {date_range_str}: {downloaded_file}")
                    except Exception as e:
                        logger.error(f"Failed to download report for {segment}: {e}")
                        FAILED_REPORTS.append(f"{name} - {segment} - {date_range_str}")
                current_start = current_end + timedelta(days=1)
            all_downloaded_files[name] = downloaded_files
            logger.info(f'Downloaded files for {name}: {downloaded_files}')
        logger.info(f'Downloaded files for all segements: {all_downloaded_files}')

    except Exception as e:
        logger.error(f"Error while downloading reports: {e}")

    finally:
        driver.quit()
        logger.info("All tasks completed!")

        if FAILED_REPORTS:
            logger.warning(f"All reports downloaded successfully, with the exception of: {FAILED_REPORTS}")
        else:
            logger.info("All reports downloaded successfully!")


def wait_for_download(files_in_dir, timeout=60):
    """Waits for a file to fully download in the given directory."""
    end_time = time.time() + timeout
# Initial files

    while time.time() < end_time:
        current_files = set(os.listdir(Env.DOWNLOAD_DIR))
        new_file = current_files - files_in_dir  # Find newly added files

        if new_file:
            file_path = os.path.join(Env.DOWNLOAD_DIR, new_file.pop())

            # Wait for the file size to stabilize (ensures download is complete)
            prev_size = -1
            while time.time() < end_time:
                curr_size = os.path.getsize(file_path)
                if curr_size == prev_size:  # Size is stable
                    return file_path
                prev_size = curr_size
                time.sleep(1)  # Check every second

        time.sleep(1)  # Wait before checking again

    raise TimeoutError("Download did not complete within the given time.")

def main():
    """Main function to test login and report downloads."""
    test_login_only = False

    driver = setup_driver()
    try:
        login_kite(driver)
        if not test_login_only:
            logger.info("Login successful! Proceeding with downloads...")
            download_reports(driver)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
