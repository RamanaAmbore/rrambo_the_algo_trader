from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Zerodha Credentials
ZERODHA_USERNAME = "your_username"
ZERODHA_PASSWORD = "your_password"
ZERODHA_PIN = "your_pin"
APP_NAME = "Rambo"  # Name of the app

# URLs
LOGIN_URL = "https://console.zerodha.com/login/"
API_URL = "https://developers.kite.trade/apps/"

# Set up Selenium WebDriver
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # Run in headless mode (remove this for debugging)
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

try:
    # Step 1: Open Kite Console Login Page
    driver.get(LOGIN_URL)
    wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text']")))

    # Step 2: Enter Username and Password
    driver.find_element(By.XPATH, "//input[@type='text']").send_keys(ZERODHA_USERNAME)
    driver.find_element(By.XPATH, "//input[@type='password']").send_keys(ZERODHA_PASSWORD)
    driver.find_element(By.XPATH, "//button").click()

    # Step 3: Enter PIN
    wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='password']")))
    driver.find_element(By.XPATH, "//input[@type='password']").send_keys(ZERODHA_PIN)
    driver.find_element(By.XPATH, "//button").click()

    # Step 4: Navigate to Developer API Page
    wait.until(EC.url_contains("console.zerodha.com/dashboard"))
    driver.get(API_URL)

    # Step 5: Click on "Rambo" App
    wait.until(EC.presence_of_element_located((By.LINK_TEXT, APP_NAME)))
    driver.find_element(By.LINK_TEXT, APP_NAME).click()

    # Step 6: Extract API Key & Secret
    wait.until(EC.presence_of_element_located((By.XPATH, "//td[@data-title='API Key']")))
    api_key = driver.find_element(By.XPATH, "//td[@data-title='API Key']").text
    api_secret = driver.find_element(By.XPATH, "//td[@data-title='Secret']").text

    print(f"API Key: {api_key}")
    print(f"API Secret: {api_secret}")

except Exception as e:
    print(f"Error: {e}")

finally:
    driver.quit()  # Close the browser
