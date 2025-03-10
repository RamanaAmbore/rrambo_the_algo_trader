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

from utils.date_time_utils import today_indian
from utils.db_connect import DbConnect
from utils.logger import get_logger
from utils.parms import Parms, sc
from utils.utils_func import generate_totp

logger = get_logger(__name__)  # Initialize logger


def setup_driver():
    """Setup Firefox WebDriver with auto-download settings."""
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    # Set Download Preferences
    download_path = os.path.abspath(Parms.DOWNLOAD_DIR)
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


def login_kite(driver, user, credential):
    """Automates Zerodha Kite login using Selenium (Firefox)."""
    logger.info("🔹 Logging into Zerodha Kite...")

    driver.get("https://kite.zerodha.com/")
    time.sleep(1)

    try:
        userid_field = driver.find_element(By.ID, "userid")
        highlight_element(driver, userid_field)
        userid_field.send_keys(user)
        logger.info("Entered User ID.")

        password_field = driver.find_element(By.ID, "password")
        highlight_element(driver, password_field)
        password_field.send_keys(credential['PASSWORD'])
        logger.info("Entered Password.")

        login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
        highlight_element(driver, login_button)
        login_button.click()
        logger.info("Submitted login credentials.")

        # Wait for TOTP field
        WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH, "//input[@type='number']")))
        totp_field = driver.find_element(By.XPATH, "//input[@type='number']")
        highlight_element(driver, totp_field)

        for attempt in range(sc.MAX_TOTP_CONN_RETRY_COUNT):
            ztotp = generate_totp(credential['TOTP_TOKEN'])
            logger.info(f"🔹 Generated TOTP: {ztotp}")
            totp_field.send_keys(ztotp)
            time.sleep(2)

            if "dashboard" in driver.current_url:
                logger.info(f"Login Successful for user: {user}")
                return
            else:
                logger.warning("Invalid TOTP! Retrying for user: {user}...")
                time.sleep(1)

    except Exception as e:
        logger.error(f"Login Failed for user{user} with exception: {e}")
        raise


def download_reports(driver, report_start_date, report_end_date, download_flags, failed_reports):
    """Downloads reports from Zerodha Console."""
    os.makedirs(Parms.DOWNLOAD_DIR, exist_ok=True)
    all_downloaded_files = {}
    max_selenium_retries = Parms.MAX_SELENIUM_RETRIES
    try:
        for name, item in sc.DOWNLOAD_REPORTS.items():
            if not download_flags.get(name, False):
                continue

            logger.info(f"Downloading: {name}")
            driver.get(item['url'])
            time.sleep(1)
            downloaded_files = {}
            current_start = report_start_date
            while current_start < report_end_date:
                current_end = min(current_start + timedelta(days=364), report_end_date)

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
                            if counter > max_selenium_retries:
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
                            if counter > max_selenium_retries:
                                logger.error(f"Dropdown selection failed for {item['P&L']['element']}: {e}")
                                continue  # Skip to the next segment if selection fails

                        date_range_str = ""
                        try:
                            date_range = WebDriverWait(driver, 10).until(
                                ec.element_to_be_clickable((By.XPATH, item['date_range'])))
                            highlight_element(driver, date_range)

                            date_range_str = date_range.get_attribute("value")
                            date_range_str = f'{current_start.strftime("%Y-%m-%d")}{date_range_str[10:13]}{current_end.strftime("%Y-%m-%d")}'
                            date_range.send_keys(Keys.CONTROL + "a")  # Select all text
                            date_range.send_keys(Keys.DELETE)  # Delete selected text
                            date_range.send_keys(date_range_str)
                            date_range.send_keys(Keys.ENTER)
                            logger.info(f"Applied date filter {date_range_str} for {segment}")
                        except Exception as e:
                            if counter > max_selenium_retries:
                                logger.error(f"Failed to set date range: {date_range_str} for {segment}: {e}")
                                continue  # Skip to the next segment if date range setting fails

                        try:
                            arrow_button = WebDriverWait(driver, 10).until(
                                ec.element_to_be_clickable((By.XPATH, item['button'])))
                            highlight_element(driver, arrow_button)
                            arrow_button.click()
                            download_csv_link = WebDriverWait(driver, 10).until(
                                ec.element_to_be_clickable((By.XPATH, item['href'])))
                            highlight_element(driver, download_csv_link)
                            files_in_dir = set(os.listdir(Parms.DOWNLOAD_DIR))
                            download_csv_link.click()
                            time.sleep(1)
                            if check_for_error_text_js(driver):
                                break

                            # Wait for the file to appear in the download directory
                            downloaded_file = wait_for_download(files_in_dir)
                            downloaded_files[segment] = downloaded_files[segment] + downloaded_file
                            logger.info(f"Download completed for {segment} for {date_range_str}: {downloaded_file}")
                            break
                        except Exception as e:
                            if counter > max_selenium_retries:
                                logger.error(f"Failed to download report for {segment}: {e}")
                                failed_reports.append(f"{name} - {segment} - {date_range_str}")
                                break
                current_start = current_end + timedelta(days=1)
            all_downloaded_files[name] = downloaded_files
            logger.info(f'Downloaded files for {name}: {downloaded_files}')
        logger.info(f'Downloaded files for all segments: {all_downloaded_files}')

    except Exception as e:
        logger.error(f"Error while downloading reports: {e}")

    finally:
        logger.info("All tasks completed!")

        if failed_reports:
            logger.warning(f"All reports downloaded successfully, with the exception of: {failed_reports}")
        else:
            logger.info("All reports downloaded successfully!")


def check_for_error_text_js(driver):
    """Returns True if 'something went wrong' or 'empty' is present anywhere in the page source."""
    return driver.execute_script(
        "return document.body.innerText.includes('something went wrong') || document.body.innerText.includes(\"Report's empty\");"
    )


def wait_for_download(files_in_dir, timeout=60):
    end_time = time.time() + timeout
    while time.time() < end_time:
        new_files = set(os.listdir(Parms.DOWNLOAD_DIR)) - files_in_dir
        for file in new_files:
            if not (file.endswith(".crdownload") or file.endswith(".part")):
                return file
        time.sleep(1)
    raise TimeoutError("Download did not complete within the timeout period.")


def login_download_reports():
    """Main function to test login and report downloads."""
    # 🔹 Constants
    DbConnect.initialize_parameters()
    report_start_date = Parms.REPORT_START_DATE
    if report_start_date is None:
        report_start_date = today_indian() - timedelta(Parms.REPORT_LOOKBACK_DAYS)
    else:
        report_start_date = datetime(int(report_start_date[:4]), int(report_start_date[5:7]),
                                     int(report_start_date[9:])).date()

    report_end_date = today_indian()

    # 🔹 Flags for enabling/disabling downloads
    download_flags = {"DOWNLOAD_TRADEBOOK": Parms.DOWNLOAD_TRADEBOOK, "DOWNLOAD_PNL": Parms.DOWNLOAD_PNL,
                      "DOWNLOAD_LEDGER": Parms.DOWNLOAD_LEDGER}

    logger.info(f'Report start date: {report_start_date}')
    logger.info(f'Report end date: {report_end_date}')
    logger.info(f'Report list: {download_flags}')

    failed_reports = []  # Track failed downloads

    for user, credential in Parms.USER_CREDENTIALS.items():
        driver = setup_driver()
        try:
            login_kite(driver, user, credential)
            logger.info("Login successful! Proceeding with downloads...")
            download_reports(driver, report_start_date, report_end_date, download_flags, failed_reports)
        finally:
            if driver is not None: driver.quit()


if __name__ == "__main__":
    login_download_reports()
