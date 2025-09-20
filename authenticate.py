"""Create login credentials for Strava.com and save them as cookies"""

import os
import pickle
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By


def authenticate():
    """Login to Strava and save the authentication cookies to a file, so we can reuse it later"""
    STRAVA_USERNAME = os.getenv("STRAVA_USERNAME")
    STRAVA_PASSWORD = os.getenv("STRAVA_PASSWORD")

    # Initialize Chrome browser with Selenium
    driver = webdriver.Firefox()

    # Open Strava login page
    driver.get("https://www.strava.com/login")

    # Give time for the page to load
    sleep(5)

    # --- Step 1: enter email ---
    driver.find_element(By.ID, "desktop-email").click()
    driver.find_element(By.ID, "desktop-email").send_keys(STRAVA_USERNAME)
    driver.find_element(By.ID, "desktop-login-button").click()

    sleep(5)

    driver.find_element(By.CSS_SELECTOR, ".DesktopLayout_desktopPanel__OKWGk .Button_text__d_3rf").click()

    sleep(5)

    driver.find_element(By.CSS_SELECTOR, ".DesktopLayout_desktopPanel__OKWGk .Input_input__zN25R").click()
    driver.find_element(By.CSS_SELECTOR, ".DesktopLayout_desktopPanel__OKWGk .Input_input__zN25R").send_keys(STRAVA_PASSWORD)
    driver.find_element(By.CSS_SELECTOR, ".DesktopLayout_desktopPanel__OKWGk .OTPCTAButton_ctaButtonContainer__b2rKX > .Button_btn__EdK33").click()

    sleep(5)

    # --- Step 4: Save Cookies ---
    with open("cookies.pkl", "wb") as file:
        pickle.dump(driver.get_cookies(), file)

    driver.close()


def main():
    """Main function"""
    authenticate()


if __name__ == "__main__":
    main()
