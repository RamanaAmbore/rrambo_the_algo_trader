import asyncio
import os
import time
from datetime import timedelta, datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

from threads.load_reports import load_reports
from utils.fetch_parms import Parm, sc
from utils.date_time_utils import today_indian
from utils.logger import get_logger
from utils.utils_func import generate_totp

logger = get_logger(__name__)  # Initialize logger

# 🔹 Constants

REPORT_START_DATE = Parm.REPORT_START_DATE
if REPORT_START_DATE is None:
    REPORT_START_DATE = today_indian() - timedelta(Parm.REPORT_LOOKBACK_DAYS)
else:
    REPORT_START_DATE = datetime(int(REPORT_START_DATE[:4]), int(REPORT_START_DATE[5:7]),
                                 int(REPORT_START_DATE[9:])).date()

REPORT_END_DATE = today_indian()

# 🔹 Flags for enabling/disabling downloads
DOWNLOAD_FLAGS = {"ReportTradebook": Parm.DOWNLOAD_TRADEBBOOK, "P&L": Parm.DOWNLOAD_PL, "Ledger": Parm.DOWNLOAD_LEDGER,
                  "Holdings": Parm.DOWNLOAD_HOLDINGS, "Positions": Parm.DOWNLOAD_POSITIONS, }

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
    download_path = os.path.abspath(Parm.DOWNLOAD_DIR)
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
        userid_field.send_keys(Parm.ZERODHA_USERNAME)
        logger.info("Entered User ID.")

        password_field = driver.find_element(By.ID, "password")
        highlight_element(driver, password_field)
        password_field.send_keys(Parm.ZERODHA_PASSWORD)
        logger.info("Entered Password.")

        login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
        highlight_element(driver, login_button)
        login_button.click()
        logger.info("Submitted login credentials.")

        # Wait for TOTP field
        WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH, "//input[@type='number']")))
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
    os.makedirs(Parm.DOWNLOAD_DIR, exist_ok=True)
    all_downloaded_files = {}
    try:
        for name, item in sc.DOWNLOAD_REPORTS.items():
            if not DOWNLOAD_FLAGS.get(name, False):
                continue

            logger.info(f"Downloading: {name}")
            driver.get(item['url'])
            time.sleep(2)
            downloaded_files = {}
            current_start = REPORT_START_DATE
            while current_start < REPORT_END_DATE:
                current_end = min(current_start + timedelta(days=364), REPORT_END_DATE)

                for segment in item['segment']['values']:  # Select both segments
                    counter = 0
                    while True:
                        counter += 1
                        try:
                            if segment not in downloaded_files:
                                downloaded_files[segment] = ""
                            dropdown = WebDriverWait(driver, 10).until(
                                ec.presence_of_element_located((By.XPATH, item['segment']['element'])))
                            highlight_element(driver, dropdown)
                            select = Select(dropdown)
                            select.select_by_visible_text(segment)
                            logger.info(f"Selected {segment} in dropdown.")
                        except Exception as e:
                            if counter <= 3: continue
                            logger.error(f"Dropdown selection failed for {segment}: {e}")
                            continue  # Skip to the next segment if selection fails

                        try:
                            if item['P&L'] is not None:
                                dropdown = WebDriverWait(driver, 10).until(
                                    ec.presence_of_element_located((By.XPATH, item['P&L']['element'])))
                                highlight_element(driver, dropdown)
                                select = Select(dropdown)
                                select.select_by_visible_text(item['P&L']['values'][0])
                                logger.info(f"Selected {item['P&L']['element']} in dropdown.")
                        except Exception as e:
                            if counter <= 3: continue
                            logger.error(f"Dropdown selection failed for {item['P&L']['element']}: {e}")
                            continue  # Skip to the next segment if selection fails

                        date_range_str = ""
                        try:
                            date_range = WebDriverWait(driver, 10).until(
                                ec.element_to_be_clickable((By.XPATH, item['date_range'])))
                            highlight_element(driver, date_range)
                            time.sleep(2)

                            date_range_str = date_range.get_attribute("value")
                            date_range_str = f'{current_start.strftime("%Y-%m-%d")}{date_range_str[10:13]}{current_end.strftime("%Y-%m-%d")}'
                            date_range.send_keys(Keys.CONTROL + "a")  # Select all text
                            date_range.send_keys(Keys.DELETE)  # Delete selected text
                            date_range.send_keys(date_range_str)
                            date_range.send_keys(Keys.ENTER)
                        except Exception as e:
                            if counter <= 3: continue
                            logger.error(f"Failed to set date range: {date_range_str} for {segment}: {e}")
                            continue  # Skip to the next segment if date range setting fails

                        try:
                            arrow_button = WebDriverWait(driver, 10).until(
                                ec.element_to_be_clickable((By.XPATH, item['button'])))
                            highlight_element(driver, arrow_button)
                            arrow_button.click()
                            logger.info(f"Applied date filter {date_range_str} for {segment}")
                            download_csv_link = WebDriverWait(driver, 10).until(
                                ec.element_to_be_clickable((By.XPATH, item['href'])))
                            highlight_element(driver, download_csv_link)
                            files_in_dir = set(os.listdir(Parm.DOWNLOAD_DIR))
                            download_csv_link.click()

                            # Wait for the file to appear in the download directory
                            if not check_for_error_text_js(driver):
                                downloaded_file = wait_for_download(files_in_dir)
                                downloaded_files[segment] = downloaded_files[segment] + downloaded_file
                            logger.info(f"Download completed for {segment} for {date_range_str}: {downloaded_file}")
                            break
                        except Exception as e:
                            if counter > 3:
                                logger.error(f"Failed to download report for {segment}: {e}")
                                FAILED_REPORTS.append(f"{name} - {segment} - {date_range_str}")
                                break
                current_start = current_end + timedelta(days=1)
            all_downloaded_files[name] = downloaded_files
            logger.info(f'Downloaded files for {name}: {downloaded_files}')
        logger.info(f'Downloaded files for all segments: {all_downloaded_files}')

    except Exception as e:
        logger.error(f"Error while downloading reports: {e}")

    finally:
        driver.quit()
        logger.info("All tasks completed!")

        if FAILED_REPORTS:
            logger.warning(f"All reports downloaded successfully, with the exception of: {FAILED_REPORTS}")
        else:
            logger.info("All reports downloaded successfully!")


def check_for_error_text_js(driver):
    """Returns True if 'something went wrong' or 'empty' is present anywhere in the page source."""
    return driver.execute_script(
        "return document.body.innerText.includes('something went wrong') || document.body.innerText.includes(\"Report's empty\");"
    )


def wait_for_download(files_in_dir, timeout=60):
    """Waits for a file to fully download in the given directory."""
    end_time = time.time() + timeout
    # Initial files

    while time.time() < end_time:
        current_files = set(os.listdir(Parm.DOWNLOAD_DIR))
        new_file = current_files - files_in_dir  # Find newly added files

        if new_file:
            file_path = os.path.join(Parm.DOWNLOAD_DIR, new_file.pop())

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


def login_download_reports():
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
    login_download_reports()
    asyncio.run(load_reports())
