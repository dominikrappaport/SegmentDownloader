"""Create login credentials for Strava.com and save them as cookies.

Written by Dominik Rappaport, dominik@rappaport.at, 2024
"""

import os
import pickle
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By

from .constants import FILENAME_COOKIES


def authenticate():
    """Login to Strava and save the authentication cookies to a file, so we can reuse it later."""
    strava_username = os.getenv("STRAVA_USERNAME")
    strava_password = os.getenv("STRAVA_PASSWORD")

    if not strava_username or not strava_password:
        raise ValueError(
            "STRAVA_USERNAME and STRAVA_PASSWORD environment variables must be set"
        )

    # Initialize Firefox browser with Selenium
    driver = webdriver.Firefox()

    try:
        # Open Strava login page
        driver.get("https://www.strava.com/login")

        # Give time for the page to load
        sleep(5)

        # --- Step 1: enter email ---
        driver.find_element(By.ID, "desktop-email").click()
        driver.find_element(By.ID, "desktop-email").send_keys(strava_username)
        driver.find_element(By.ID, "desktop-login-button").click()

        sleep(5)

        driver.find_element(
            By.CSS_SELECTOR, ".DesktopLayout_desktopPanel__OKWGk .Button_text__d_3rf"
        ).click()

        sleep(5)

        driver.find_element(
            By.CSS_SELECTOR, ".DesktopLayout_desktopPanel__OKWGk .Input_input__zN25R"
        ).click()
        driver.find_element(
            By.CSS_SELECTOR, ".DesktopLayout_desktopPanel__OKWGk .Input_input__zN25R"
        ).send_keys(strava_password)
        driver.find_element(
            By.CSS_SELECTOR,
            ".DesktopLayout_desktopPanel__OKWGk .OTPCTAButton_ctaButtonContainer__b2rKX > .Button_btn__EdK33",
        ).click()

        sleep(5)

        # --- Step 4: Save Cookies ---
        with open(FILENAME_COOKIES, "wb") as file:
            pickle.dump(driver.get_cookies(), file)
    finally:
        driver.close()


def main():
    """Main function for CLI entry point."""
    try:
        authenticate()
        print(f"Authentication successful! Cookies saved to {FILENAME_COOKIES}")
    except ValueError as exc:
        print(f"Error: {exc}")
        exit(1)
    except Exception as exc:
        print(f"Authentication failed: {exc}")
        exit(1)


if __name__ == "__main__":
    main()
