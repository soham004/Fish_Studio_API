from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import *
import time
import json

def loginToFish(driver:webdriver.Chrome, fishEmail:str, fishPassword:str):

    """
    This function logs into fish.audio and waits for 10 seconds for the login to finish.
    """
    emailField = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@type="email"]')))
    emailField.send_keys(Keys.CONTROL + "a")
    emailField.send_keys(Keys.DELETE)
    emailField.send_keys(fishEmail)
    passwordField = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@type="password"]')))
    passwordField.send_keys(Keys.CONTROL + "a")
    passwordField.send_keys(Keys.DELETE)
    passwordField.send_keys(fishPassword)
    loginButton = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(),'Login')]")))
    loginButton.click()
    try:
        playgroundText = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, '//span[contains(text(),"Playground")]')))
        print("Login Successful")
        return
    except TimeoutException:
        print("Reloading..")
        driver.get("https://fish.audio/")
        try:
            playgroundText = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, '//span[contains(text(),"Playground")]')))
            print("Login Successful")
            return
        except TimeoutException:
            print("Login Failed. Please check your credentials in the config file.")
            # sys.exit()

def get_token_from_browser_logs(logs):
    """
    Return only logs which have a method that start with "Network.response", "Network.request", or "Network.webSocket"
    and contain an Authorization header with a Bearer token.
    """
    bearer_token = None

    for entry in logs:
        log = json.loads(entry["message"])["message"]
        if (
            "Network.response" in log["method"]
            or "Network.request" in log["method"]
            or "Network.webSocket" in log["method"]
        ):
            # Check if headers exist and contain an Authorization header
            headers = log.get("params", {}).get("request", {}).get("headers", {})
            authorization = headers.get("Authorization") or headers.get("authorization")
            if authorization and authorization.startswith("Bearer ") and not authorization.startswith("Bearer tokenNotNeeded"):
                bearer_token = authorization.split(" ")[1]

    return bearer_token

def fetch_bearer_using_selenium(email:str, password:str) -> str:
    options = webdriver.ChromeOptions()
    # if muteBrowser:
    prefs = {
         'profile.default_content_setting_values.automatic_downloads': 1,
         "download.prompt_for_download" : False,
         "download.directory_upgrade": True,
         "plugins.always_open_pdf_externally": True,
         "safebrowsing.enabled": True,
         "safebrowsing.disable_download_protection": True,
        }
    options.add_argument("--mute-audio"); #// Mute audio
    options.add_experimental_option("prefs",prefs)
    options.add_argument("start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled") 
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False) 
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_experimental_option("prefs", prefs) 
    options.add_argument('log-level=3')
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    stealth(
        driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Google Inc. (Intel)",
        renderer="ANGLE (Intel, Intel(R) Iris(R) Xe Graphics (0x000046A8) Direct3D11 vs_5_0 ps_5_0, D3D11)",
        fix_hairline=True,
    )

    driver.get("https://fish.audio/auth/")

    loginToFish(driver, email, password)

    

    # Wait a few seconds to ensure all requests are done
    time.sleep(5)

    logs = driver.get_log('performance')

    token = get_token_from_browser_logs(logs)
    if token:
        print("Bearer token fetched successfully.")
        driver.quit()
        return token
    else:
        print("Failed to fetch bearer token.")



    