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

from src.core.database_manager import DatabaseManager as Db
from src.utils.date_time_utils import today_indian
from src.utils.logger import get_logger
from src.settings.parameter_manager import ParameterManager as Parm, sc
from src.utils.utils import generate_totp, delete_folder_contents

logger = get_logger(__name__)  # Initialize logger
Db.initialize_parameters()


class ReportDownloader:
    driver = None
    report_start_date = None
    report_end_date = None
    user = None
    credential = None
    failed_reports = []  # Track failed downloads
    download_path = None
    refresh_reports = None

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

    @classmethod
    def login_kite(cls):
        """Automates Zerodha Kite login using Selenium (Firefox)."""
        logger.info("Logging into Zerodha Kite for user {cls.user}...")

        cls.driver.get(Parm.KITE_URL)
        WebDriverWait(cls.driver, 5).until(EC.presence_of_element_located((By.ID, "userid")))

        try:
            userid_field = cls.driver.find_element(By.ID, "userid")
            cls.highlight_element(userid_field)
            userid_field.send_keys(cls.user)
            logger.info(f"Entered User ID for {cls.user}")

            password_field = cls.driver.find_element(By.ID, "password")
            cls.highlight_element(password_field)
            password_field.send_keys(cls.credential['PASSWORD'])
            logger.info(f"Entered Password for {cls.user}")

            login_button = cls.driver.find_element(By.XPATH, '//button[@type="submit"]')
            cls.highlight_element(login_button)
            login_button.click()
            logger.info(f"Submitted login credentials for {cls.user}")

            # Wait for TOTP field
            WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@type='number']")))
            totp_field = cls.driver.find_element(By.XPATH, "//input[@type='number']")
            cls.highlight_element(totp_field)

            for attempt in range(sc.MAX_TOTP_CONN_RETRY_COUNT):
                ztotp = generate_totp(cls.credential['TOTP_TOKEN'])
                logger.info(f"Generated TOTP: {ztotp}")
                totp_field.send_keys(ztotp)
                # Wait for dashboard URL change
                WebDriverWait(cls.driver, 3).until(lambda d: "dashboard" in d.current_url)

                if "dashboard" in cls.driver.current_url:
                    logger.info(f"Login Successful for user {cls.user}")
                    return
                else:
                    logger.warning(
                        f"Invalid TOTP! Retrying for user: {cls.user} (Attempt {attempt + 1}/{sc.MAX_TOTP_CONN_RETRY_COUNT})")
                if attempt == sc.MAX_TOTP_CONN_RETRY_COUNT - 1:
                    raise ValueError(f"TOTP Authentication Failed for user {cls.user}")

        except Exception as e:
            msg = f"Login Failed for user{cls.user} with exception: {e}"
            logger.error(msg)
            raise Exception(msg)

    @classmethod
    def download_reports(cls):
        """Downloads reports from Zerodha Console and returns a dictionary of downloaded files."""
        os.makedirs(Parm.DOWNLOAD_DIR, exist_ok=True)
        all_downloaded_files = {}
        max_selenium_retries = Parm.MAX_SELENIUM_RETRIES

        for name, item in sc.REPORTS_PARM.items():
            if not cls.refresh_reports.get(name, False):
                continue

            logger.info(f"Downloading: {name}")
            cls.driver.get(item['url'])
            WebDriverWait(cls.driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            downloaded_files = {}
            current_start = cls.report_start_date
            while current_start < cls.report_end_date:
                current_end = min(current_start + timedelta(days=364), cls.report_end_date)

                for segment in item['segment']['values']:  # Select both segments

                    for counter in range(1, max_selenium_retries + 1):
                        date_range_str = ""
                        try:
                            cls.select_segment(downloaded_files, item, segment)

                            cls.select_pnl_element(item)

                            date_range_str = cls.enter_date_range(current_start, current_end, item, segment)

                            arrow_button = WebDriverWait(cls.driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, item['button'])))
                            cls.highlight_element(arrow_button)
                            arrow_button.click()
                            if cls.check_for_error_text_js(current_start.strftime("%Y-%m-%d")):
                                break
                            download_csv_link = WebDriverWait(cls.driver, 15).until(
                                EC.element_to_be_clickable((By.XPATH, item['href'])))
                            cls.highlight_element(download_csv_link)
                            cls.files_in_dir = set(os.listdir(Parm.DOWNLOAD_DIR))
                            download_csv_link.click()
                            time.sleep(1)

                            downloaded_file = cls.wait_for_download()
                            downloaded_files[segment].append(downloaded_file)
                            logger.info(f"Download completed for {segment} ({date_range_str}): {downloaded_file}")
                            break
                        except Exception:
                            logger.error(f"Download failed for {name} {cls.user} - {segment} - ({date_range_str})")

                current_start = current_end + timedelta(days=1)
            all_downloaded_files[name] = downloaded_files
        logger.info(f'Downloaded files for {cls.user} all segments: {all_downloaded_files}')

        if not all_downloaded_files:
            logger.warning("No reports were downloaded.")
        return all_downloaded_files

    @classmethod
    def enter_date_range(cls, current_start, current_end, item, segment):
        date_range = WebDriverWait(cls.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, item['date_range'])))
        cls.highlight_element(date_range)
        date_range_str = f'{current_start.strftime("%Y-%m-%d")} to {current_end.strftime("%Y-%m-%d")}'
        date_range.send_keys(Keys.CONTROL + "a")
        date_range.send_keys(Keys.DELETE)
        date_range.send_keys(date_range_str)
        date_range.send_keys(Keys.ENTER)
        logger.info(f"Applied date filter {date_range_str} for {segment}")
        return date_range_str

    @classmethod
    def select_pnl_element(cls, item):
        if item['P&L'] is not None:
            dropdown = WebDriverWait(cls.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, item['P&L']['element'])))
            cls.highlight_element(dropdown)
            select = Select(dropdown)
            select.select_by_visible_text(item['P&L']['values'][0])
            logger.info(f"Selected {item['P&L']['element']} in dropdown.")

    @classmethod
    def select_segment(cls, downloaded_files, item, segment):
        if segment not in downloaded_files:
            downloaded_files[segment] = []
        dropdown = WebDriverWait(cls.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, item['segment']['element'])))
        cls.highlight_element(dropdown)
        select = Select(dropdown)
        select.select_by_visible_text(segment)
        logger.info(f"Selected {segment} in dropdown.")

    @classmethod
    def check_for_error_text_js(cls, current_start_str):
        """Returns True if 'something went wrong' or 'empty' is present anywhere in the page source."""

        result = not cls.driver.execute_script(f"return document.body.innerText.includes('{current_start_str}');")

        if result:
            logger.warning('Report is empty or something went wrong')
        return result

    @classmethod
    def wait_for_download(cls, timeout=60):
        end_time = time.time() + timeout
        while time.time() < end_time:
            new_files = set(os.listdir(Parm.DOWNLOAD_DIR)) - cls.files_in_dir
            for file in new_files:
                if not (file.endswith(".crdownload") or file.endswith(".part")):
                    return file
        raise TimeoutError("Download did not complete within the timeout period.")

    @classmethod
    def login_download_reports(cls):
        """Login and download reports for multiple users, returning a dictionary of downloaded files."""
        cls.initialize()
        user_downloads = {}

        for user, credential in Parm.USER_CREDENTIALS.items():
            cls.user = user
            cls.credential = credential
            cls.setup_driver()
            try:
                cls.login_kite()
                logger.info(f"Proceeding with downloads for user {cls.user}...")
                user_downloads[user] = cls.download_reports()  # Store downloaded files for each user
            finally:
                if cls.driver is not None:
                    cls.driver.quit()

        return user_downloads  # Return dictionary of downloaded files per user

    @classmethod
    def initialize(cls):

        cls.download_path = os.path.abspath(Parm.DOWNLOAD_DIR)
        delete_folder_contents(cls.download_path)

        cls.report_start_date = Parm.REPORT_START_DATE
        if cls.report_start_date is None:
            cls.report_start_date = today_indian() - timedelta(Parm.REPORT_LOOKBACK_DAYS)
        else:
            cls.report_start_date = datetime(int(cls.report_start_date[:4]), int(cls.report_start_date[5:7]),
                                             int(cls.report_start_date[8:])).date()
        cls.report_end_date = today_indian()

        cls.refresh_reports = {"TRADEBOOK": Parm.REFRESH_TRADEBOOK,
                               "PNL": Parm.REFRESH_PNL,
                               "LEDGER": Parm.REFRESH_LEDGER}

        logger.info(f'Report start date: {cls.report_start_date}')
        logger.info(f'Report end date: {cls.report_end_date}')
        logger.info(f'Report list: {cls.refresh_reports}')


if __name__ == "__main__":
    downloaded_reports = ReportDownloader.login_download_reports()
    print(downloaded_reports)  # Print downloaded files for debugging
