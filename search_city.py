from time import sleep
import os
import pandas as pd
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
record = None

def get_page_with_retries(driver, url, max_attempts=3):
    for attempt in range(1, max_attempts + 1):
        try:
            driver.get(url)
            return True  # the page loaded, so stop retrying
        except (TimeoutException, WebDriverException) as e:
            print(f'Attempt {attempt} failed: {type(e).__name__}')
            if attempt < max_attempts:
                wait = 2 * attempt  # wait longer after each failure: 2 seconds, then 4 seconds
                print(f'Waiting {wait} seconds before the next attempt')
                sleep(wait)
    print(f'Giving up on {url} after {max_attempts} attempts.')
    return False

def search_city(driver, query):
    box = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'form.tad-hero-search__search input[name="query"]'))
    )
    box.clear()
    box.send_keys(query)
    sleep(1)  # let any suggestion list finish loading
    driver.find_element(By.CSS_SELECTOR, 'form.tad-hero-search__search button.tad-search__button').click()
    sleep(3)
    print("After search:", driver.current_url)

def open_city_page(driver):
    if "/weather/usa/" in driver.current_url:
        return  # already on a city page
    try:
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//a[contains(., 'Cary') and "
                "(contains(., 'North Carolina') or contains(., 'NC'))]",
            ))
        ).click()
        sleep(3)
    except TimeoutException:
        print("Could not find a Cary, North Carolina link in the results.")

def get_text(driver, selector):
    try:
        return driver.find_element(By.CSS_SELECTOR, selector).text.strip()
    except NoSuchElementException:
        return ""


def value_after_label(driver, label):
    """Read a detail (e.g. Humidity) from a th/td pair. '' if missing."""
    try:
        return driver.find_element(
            By.XPATH, f"//th[normalize-space()='{label}']/following-sibling::td[1]"
        ).text.strip()
    except NoSuchElementException:
        return ""

def scrape_city(driver, query):
    return {
        "query": query,
        "url": driver.current_url,
        "temperature": get_text(driver, '#qlook .h2'),
        "conditions": get_text(driver, '#qlook p'),
        "visibility": value_after_label(driver, "Visibility"),
        "pressure": value_after_label(driver, "Pressure"),
        "humidity": value_after_label(driver, "Humidity"),
        "dew_point": value_after_label(driver, "Dew Point"),
    }

try:
    if get_page_with_retries(driver, 'https://www.timeanddate.com/weather/'):
        print(driver.title)
        search_city(driver, 'Cary, North Carolina')
        open_city_page(driver)
        print("City page:", driver.current_url)
        record = scrape_city(driver, 'Cary, North Carolina')
finally:
    driver.quit()

if record:
    df = pd.DataFrame([record])
    print(df.T)  # transposed so each field is on its own line

    os.makedirs("data", exist_ok=True)
    df.to_csv('data/raw_cary.csv', index=False)
    print(f"Saved {'data/raw_cary.csv'}")