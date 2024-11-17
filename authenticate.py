"""Create login credentials for Strava.com and save them as cookies"""

import pickle
import time
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def authenticate():
    """Login to Strava and save the authentication cookies to a file, so we can reuse it later"""
    email = os.getenv("STRAVA_USERNAME")
    password = os.getenv("STRAVA_PASSWORD")

    # Initialize Chrome browser with Selenium
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    # Open Strava login page
    driver.get("https://www.strava.com/login")

    # Give time for the page to load
    time.sleep(3)

    # Find the email and password input fields and log in
    email_field = driver.find_element(By.ID, "email")
    password_field = driver.find_element(By.ID, "password")

    # Enter your credentials
    email_field.send_keys(email)
    password_field.send_keys(password)

    # Submit the form by simulating pressing the Enter key
    password_field.send_keys(Keys.RETURN)

    # Wait for a while to let the login process complete (adjust as needed)
    time.sleep(3)

    with open("cookies.pkl", "wb") as file:
        pickle.dump(driver.get_cookies(), file)


def main():
    """Main function"""
    authenticate()


if __name__ == "__main__":
    main()
