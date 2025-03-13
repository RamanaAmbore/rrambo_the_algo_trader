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
from src.utils.parameter_manager import ParameterManager as Parm, sc

from src.utils.utils import delete_folder_contents
from src.utils.utils import generate_totp

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
    download_flags = None

    @classmethod
    def __initialize(cls):

        cls.download_path = os.path.abspath(Parm.DOWNLOAD_DIR)
        delete_folder_contents(cls.download_path)

        cls.report_start_date = Parm.REPORT_START_DATE
        if cls.report_start_date is None:
            cls.report_start_date = today_indian() - timedelta(Parm.REPORT_LOOKBACK_DAYS)
        else:
            cls.report_start_date = datetime(int(cls.report_start_date[:4]), int(cls.report_start_date[5:7]),
                                             int(cls.report_start_date[8:])).date()
        cls.report_end_date = today_indian()

        cls.download_flags = {"TRADEBOOK": Parm.TRADEBOOK,
                              "PNL": Parm.PNL,
                              "LEDGER": Parm.LEDGER}

        logger.info(f'Report start date: {cls.report_start_date}')
        logger.info(f'Report end date: {cls.report_end_date}')
        logger.info(f'Report list: {cls.download_flags}')

    @classmethod
    def __setup_driver(cls):
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
    def __download_reports(cls):
        """Downloads reports from Zerodha Console and returns a dictionary of downloaded files."""
        os.makedirs(Parm.DOWNLOAD_DIR, exist_ok=True)
        all_downloaded_files = {}
        max_selenium_retries = Parm.MAX_SELENIUM_RETRIES

        for name, item in sc.DOWNLOAD_REPORTS.items():
            if not cls.download_flags.get(name, False):
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
                            cls.__select_segment(downloaded_files, item, segment)

                            cls.__select_pnl_element(item)

                            date_range_str = cls.__enter_date_range(current_end, current_start, item, segment)

                            arrow_button = WebDriverWait(cls.driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, item['button'])))
                            highlight_element(cls.driver, arrow_button)
                            arrow_button.click()
                            if cls.__check_for_error_text_js():
                                break
                            download_csv_link = WebDriverWait(cls.driver, 15).until(
                                EC.element_to_be_clickable((By.XPATH, item['href'])))
                            highlight_element(cls.driver, download_csv_link)
                            cls.files_in_dir = set(os.listdir(Parm.DOWNLOAD_DIR))
                            download_csv_link.click()
                            time.sleep(1)

                            downloaded_file = cls.__wait_for_download()
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
    def __enter_date_range(cls, current_end, current_start, item, segment):
        date_range = WebDriverWait(cls.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, item['date_range'])))
        highlight_element(cls.driver, date_range)
        date_range_str = f'{current_start.strftime("%Y-%m-%d")} to {current_end.strftime("%Y-%m-%d")}'
        date_range.send_keys(Keys.CONTROL + "a")
        date_range.send_keys(Keys.DELETE)
        date_range.send_keys(date_range_str)
        date_range.send_keys(Keys.ENTER)
        logger.info(f"Applied date filter {date_range_str} for {segment}")
        return date_range_str

    @classmethod
    def __select_pnl_element(cls, item):
        if item['P&L'] is not None:
            dropdown = WebDriverWait(cls.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, item['P&L']['element'])))
            highlight_element(cls.driver, dropdown)
            select = Select(dropdown)
            select.select_by_visible_text(item['P&L']['values'][0])
            logger.info(f"Selected {item['P&L']['element']} in dropdown.")

    @classmethod
    def __select_segment(cls, downloaded_files, item, segment):
        if segment not in downloaded_files:
            downloaded_files[segment] = []
        dropdown = WebDriverWait(cls.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, item['segment']['element'])))
        highlight_element(cls.driver, dropdown)
        select = Select(dropdown)
        select.select_by_visible_text(segment)
        logger.info(f"Selected {segment} in dropdown.")

    @classmethod
    def __check_for_error_text_js(cls):
        """Returns True if 'something went wrong' or 'empty' is present anywhere in the page source."""

        result = cls.driver.execute_script(
            "return document.body.innerText.includes('something went wrong') || "
            "document.body.innerText.includes(\"Report's empty\") || "
            "document.body.innerText.includes(\"Console under maintenance\") ;"
        )
        if result:
            logger.warning('Report is empty or something went wrong')
        return result

    @classmethod
    def __wait_for_download(cls, timeout=60):
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
        cls.__initialize()
        user_downloads = {}

        for user, credential in Parm.USER_CREDENTIALS.items():
            cls.user = user
            cls.credential = credential
            cls.__setup_driver()
            try:
                login_kite(cls.driver, cls.user, cls.credential)
                logger.info("Proceeding with downloads for user {cls.user}...")
                user_downloads[user] = cls.__download_reports()  # Store downloaded files for each user
            finally:
                if cls.driver is not None:
                    cls.driver.quit()

        return user_downloads  # Return dictionary of downloaded files per user
    
    
def login_kite(driver, user, credential):
    """Automates Zerodha Kite login using Selenium (Firefox)."""
    logger.info("Logging into Zerodha Kite for user {user}...")

    driver.get(Parm.KITE_URL)
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "userid")))

    try:
        userid_field = driver.find_element(By.ID, "userid")
        highlight_element(driver, userid_field)
        userid_field.send_keys(user)
        logger.info(f"Entered User ID for {user}")

        password_field = driver.find_element(By.ID, "password")
        highlight_element(driver, password_field)
        password_field.send_keys(credential['PASSWORD'])
        logger.info(f"Entered Password for {user}")

        login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
        highlight_element(driver, login_button)
        login_button.click()
        logger.info(f"Submitted login credentials for {user}")

        # Wait for TOTP field
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@type='number']")))
        totp_field = driver.find_element(By.XPATH, "//input[@type='number']")
        highlight_element(driver, totp_field)

        for attempt in range(sc.MAX_TOTP_CONN_RETRY_COUNT):
            ztotp = generate_totp(credential['TOTP_TOKEN'])
            logger.info(f"Generated TOTP: {ztotp}")
            totp_field.send_keys(ztotp)
            # Wait for dashboard URL change
            WebDriverWait(driver, 3).until(lambda d: "dashboard" in d.current_url)

            if "dashboard" in driver.current_url:
                logger.info(f"Login Successful for user {user}")
                return
            else:
                logger.warning(
                    f"Invalid TOTP! Retrying for user: {user} (Attempt {attempt + 1}/{sc.MAX_TOTP_CONN_RETRY_COUNT})")
            if attempt == sc.MAX_TOTP_CONN_RETRY_COUNT - 1:
                raise ValueError(f"TOTP Authentication Failed for user {user}")

    except Exception as e:
        msg = f"Login Failed for user{user} with exception: {e}"
        logger.error(msg)
        raise Exception(msg)

def highlight_element(driver, element):
    """Highlight a Selenium WebElement for debugging."""
    driver.execute_script("arguments[0].style.border='3px solid red'", element)

if __name__ == "__main__":
    downloaded_reports = ReportDownloader.login_download_reports()
    print(downloaded_reports)  # Print downloaded files for debugging
