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
from src.core.db_manager import DbManager
from src.utils.date_time_utils import today_indian

from src.utils.logger import get_logger
from src.utils.parameter_manager import ParameterManager as Parm, sc
from src.utils.utils import generate_totp, delete_folder_contents

logger = get_logger(__name__)  # Initialize logger

DbManager.initialize_parameters()
class ReportDownloader:
    driver = None
    report_start_date = None
    report_end_date = None
    user = None
    credential = None
    failed_reports = []  # Track failed downloads
    download_path = None
    download_flags = None

    @classmethod
    def setup_driver(cls):
        """Setup Firefox WebDriver with auto-download settings."""
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")

        # Set Download Preferences

        logger.info(f"Download path: {cls.download_path}")
        options.set_preference("browser.download.folderList", 2)  # Use custom directory
        options.set_preference("browser.download.dir", cls.download_path)  # Ensure absolute path
        options.set_preference("browser.download.useDownloadDir", True)
        options.set_preference("browser.download.panel.shown", False)  # Hide download panel
        options.set_preference("browser.helperApps.neverAsk.saveToDisk",
                               "text/csv,application/csv,application/vnd.ms-excel")  # Auto-download CSVs

        # Disable Built-in PDF Viewer (Prevents Download Errors)
        options.set_preference("pdfjs.disabled", True)

        cls.driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

    @classmethod
    def highlight_element(cls, element):
        """Highlight a Selenium WebElement for debugging."""
        cls.driver.execute_script("arguments[0].style.border='3px solid red'", element)
        time.sleep(0.5)

    @classmethod
    def login_kite(cls):
        """Automates Zerodha Kite login using Selenium (Firefox)."""
        logger.info("🔹 Logging into Zerodha Kite...")

        cls.driver.get("https://kite.zerodha.com/")
        time.sleep(1)

        try:
            userid_field = cls.driver.find_element(By.ID, "userid")
            cls.highlight_element(userid_field)
            userid_field.send_keys(cls.user)
            logger.info("Entered User ID.")

            password_field = cls.driver.find_element(By.ID, "password")
            cls.highlight_element(password_field)
            password_field.send_keys(cls.credential['PASSWORD'])
            logger.info("Entered Password.")

            login_button = cls.driver.find_element(By.XPATH, '//button[@type="submit"]')
            cls.highlight_element(login_button)
            login_button.click()
            logger.info("Submitted login credentials.")

            # Wait for TOTP field
            WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@type='number']")))
            totp_field = cls.driver.find_element(By.XPATH, "//input[@type='number']")
            cls.highlight_element(totp_field)

            for attempt in range(sc.MAX_TOTP_CONN_RETRY_COUNT):
                ztotp = generate_totp(cls.credential['TOTP_TOKEN'])
                logger.info(f"🔹 Generated TOTP: {ztotp}")
                totp_field.send_keys(ztotp)
                time.sleep(2)

                if "dashboard" in cls.driver.current_url:
                    logger.info(f"Login Successful for user: {cls.user}")
                    return
                else:
                    logger.warning("Invalid TOTP! Retrying for user: {user}...")
                    time.sleep(1)

        except Exception as e:
            logger.error(f"Login Failed for user{cls.user} with exception: {e}")
            raise

    @classmethod
    def download_reports(cls):
        """Downloads reports from Zerodha Console."""
        os.makedirs(Parm.DOWNLOAD_DIR, exist_ok=True)
        all_downloaded_files = {}
        max_selenium_retries = Parm.MAX_SELENIUM_RETRIES
        try:
            for name, item in sc.DOWNLOAD_REPORTS.items():
                if not cls.download_flags.get(name, False):
                    continue

                logger.info(f"Downloading: {name}")
                cls.driver.get(item['url'])
                time.sleep(1)
                downloaded_files = {}
                current_start = cls.report_start_date
                while current_start < cls.report_end_date:
                    current_end = min(current_start + timedelta(days=364), cls.report_end_date)

                    for segment in item['segment']['values']:  # Select both segments
                        counter = 0
                        while True:
                            date_range_str = ""
                            downloaded_file = ""
                            counter += 1
                            try:
                                if segment not in downloaded_files:
                                    downloaded_files[segment] = ""
                                dropdown = WebDriverWait(cls.driver, 10).until(
                                    EC.presence_of_element_located((By.XPATH, item['segment']['element'])))
                                cls.highlight_element(dropdown)
                                select = Select(dropdown)
                                select.select_by_visible_text(segment)
                                logger.info(f"Selected {segment} in dropdown.")

                                if item['P&L'] is not None:
                                    dropdown = WebDriverWait(cls.driver, 10).until(
                                        EC.presence_of_element_located((By.XPATH, item['P&L']['element'])))
                                    cls.highlight_element(dropdown)
                                    select = Select(dropdown)
                                    select.select_by_visible_text(item['P&L']['values'][0])
                                    logger.info(f"Selected {item['P&L']['element']} in dropdown.")

                                date_range_str = ""

                                date_range = WebDriverWait(cls.driver, 10).until(
                                    EC.element_to_be_clickable((By.XPATH, item['date_range'])))
                                cls.highlight_element(date_range)

                                date_range_str = date_range.get_attribute("value")
                                date_range_str = f'{current_start.strftime("%Y-%m-%d")}{date_range_str[10:13]}{current_end.strftime("%Y-%m-%d")}'
                                date_range.send_keys(Keys.CONTROL + "a")  # Select all text
                                date_range.send_keys(Keys.DELETE)  # Delete selected text
                                date_range.send_keys(date_range_str)
                                date_range.send_keys(Keys.ENTER)
                                logger.info(f"Applied date filter {date_range_str} for {segment}")

                                arrow_button = WebDriverWait(cls.driver, 10).until(
                                    EC.element_to_be_clickable((By.XPATH, item['button'])))
                                cls.highlight_element(arrow_button)
                                arrow_button.click()
                                download_csv_link = WebDriverWait(cls.driver, 10).until(
                                    EC.element_to_be_clickable((By.XPATH, item['href'])))
                                cls.highlight_element(download_csv_link)
                                cls.files_in_dir = set(os.listdir(Parm.DOWNLOAD_DIR))
                                download_csv_link.click()
                                time.sleep(1)
                                if cls.check_for_error_text_js():
                                    break

                                # Wait for the file to appear in the download directory
                                downloaded_file = cls.wait_for_download()
                                downloaded_files[segment] = downloaded_files[segment] + downloaded_file
                                logger.info(f"Download completed for {segment} for {date_range_str}: {downloaded_file}")
                                break
                            except Exception as e:
                                if counter > max_selenium_retries:
                                    if item['P&L'] is not None:
                                        logger.error(f"Dropdown selection failed for {item['P&L']['element']}: {e}")
                                    logger.error(
                                        f"Download failed for {segment} for {date_range_str}: {downloaded_file}")
                                    cls.failed_reports.append(f"{name} - {segment} - {date_range_str}")
                                    break
                    current_start = current_end + timedelta(days=1)
                all_downloaded_files[name] = downloaded_files
                logger.info(f'Downloaded files for {name}: {downloaded_files}')
            logger.info(f'Downloaded files for all segments: {all_downloaded_files}')

        except Exception as e:
            logger.error(f"Error while downloading reports: {e}")

        finally:
            logger.info("All tasks completed!")

            if cls.failed_reports:
                logger.warning(f"All reports downloaded successfully, with the exception of: {cls.failed_reports}")
            else:
                logger.info("All reports downloaded successfully!")

    @classmethod
    def check_for_error_text_js(cls):
        """Returns True if 'something went wrong' or 'empty' is present anywhere in the page source."""
        return cls.driver.execute_script(
            "return document.body.innerText.includes('something went wrong') || document.body.innerText.includes(\"Report's empty\");"
        )

    @classmethod
    def wait_for_download(cls, timeout=60):
        end_time = time.time() + timeout
        while time.time() < end_time:
            new_files = set(os.listdir(Parm.DOWNLOAD_DIR)) - cls.files_in_dir
            for file in new_files:
                if not (file.endswith(".crdownload") or file.endswith(".part")):
                    return file
            time.sleep(1)
        raise TimeoutError("Download did not complete within the timeout period.")

    @classmethod
    def login_download_reports(cls):
        """Main function to test login and report downloads."""
        # 🔹 Constants
        cls.initialize()

        for user, credential in Parm.USER_CREDENTIALS.items():
            cls.user = user
            cls.credential = credential
            cls.setup_driver()
            try:
                cls.login_kite()
                logger.info("Login successful! Proceeding with downloads...")
                cls.download_reports()
            finally:
                if cls.driver is not None: cls.driver.quit()

    @classmethod

    @classmethod
    def initialize(cls):
        DbManager.initialize_parameters()
        cls.download_path = os.path.abspath(Parm.DOWNLOAD_DIR)
        delete_folder_contents(cls.download_path)

        cls.report_start_date = Parm.REPORT_START_DATE
        if cls.report_start_date is None:
            cls.report_start_date = today_indian() - timedelta(Parm.REPORT_LOOKBACK_DAYS)
        else:
            cls.report_start_date = datetime(int(cls.report_start_date[:4]), int(cls.report_start_date[5:7]),
                                             int(cls.report_start_date[9:])).date()
        cls.report_end_date = today_indian()

        cls.download_flags = {"DOWNLOAD_TRADEBOOK": Parm.DOWNLOAD_TRADEBOOK,
                              "DOWNLOAD_PNL": Parm.DOWNLOAD_PNL,
                              "DOWNLOAD_LEDGER": Parm.DOWNLOAD_LEDGER}

        logger.info(f'Report start date: {cls.report_start_date}')
        logger.info(f'Report end date: {cls.report_end_date}')
        logger.info(f'Report list: {cls.download_flags}')


if __name__ == "__main__":
    ReportDownloader.login_download_reports()
