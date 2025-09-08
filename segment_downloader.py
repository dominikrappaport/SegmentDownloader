"""Download the full leaderboard for a given Strava segment including the categorical
information and write the results in a CSV file.

Written by Dominik Rappaport, dominik@rappaport.at, 2024
"""

import argparse
import csv
import pickle
import sys
import time
from typing import List, Dict, Tuple, Optional

from selenium import webdriver
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from selenium.webdriver.common.by import By

FILENAME_STATE = "state.pkl"
FILENAME_COOKIES = "cookies.pkl"
CATEGORIES_SEX = ["Men", "Women"]
CATEGORIES_AGE = [
    "19 and under",
    "20 to 24",
    "25 to 34",
    "35 to 44",
    "45 to 54",
    "55 to 64",
    "65 to 69",
    "70 to 74",
    "75+"]
CATEGORIES_WEIGHT = [
    "54 kg and under",
    "55 to 64 kg",
    "65 to 74 kg",
    "75 to 84 kg",
    "85 to 94 kg",
    "95 kg to 104 kg",
    "105 kg to 114 kg",
    "115 kg and over"]
LeaderBoardType = List[Dict[str, Optional[str]]]
LeaderBoardFilterType = Tuple[Optional[str], Optional[str], Optional[str]]


class SegmentDownloaderException(Exception):
    """Custom exception for the SegmentDownloader programme."""


class SegmentDownloader:
    """Implements all methods to download the leaderboard from Strava."""

    def __init__(self, segment_id: str):
        """Initialize the SegmentDownloader object.

        :param segment_id: The segment ID as a string

        :exception SegmentDownloaderException: If the driver can't be created."""
        self.segment_id: str = segment_id
        self.completed_phase: int = 0
        self.completed_page: int = 0
        self.driver: webdriver.Firefox = self.__create_driver()

        self.leaderboard_data: Dict[LeaderBoardFilterType, LeaderBoardType] = \
            {(None, None, None): []}

        for s in CATEGORIES_SEX:
            for a in CATEGORIES_AGE:
                self.leaderboard_data[(s, a, None)] = []

        for s in CATEGORIES_SEX:
            for w in CATEGORIES_WEIGHT:
                self.leaderboard_data[(s, None, w)] = []

    def __del__(self):
        """Close the driver.

        :exception SegmentDownloaderException: If the driver can't be closed."""
        try:
            self.driver.quit()
        except WebDriverException as exc:
            raise SegmentDownloaderException(f"Can't close the driver ({exc.msg}).") from exc

    def __getstate__(self):
        """Return the state of the object for pickling. We need to override this methode to
        exclude the driver object from the state."""
        state = self.__dict__.copy()
        del state["driver"]
        return state

    def __setstate__(self, state):
        """Set the state of the object for unpickling. We need to override this method to
        recreate the driver object."""
        self.__dict__.update(state)
        self.driver = self.__create_driver()

    @staticmethod
    def __create_driver() -> webdriver.Firefox:
        """Login to Strava using the cookies and return the driver.

        :return: The driver

        :exception SegmentDownloaderException: If the driver can't be created or"""
        try:
            driver: webdriver.Firefox = webdriver.Firefox()
            driver.get("https://www.strava.com")

            with open(FILENAME_COOKIES, "rb") as file:
                cookies = pickle.load(file)
                for cookie in cookies:
                    driver.add_cookie(cookie)

            return driver
        except WebDriverException as exc:
            raise SegmentDownloaderException(f"Can't create the driver ({exc.msg}).") from exc
        except (IOError, pickle.PickleError) as exc:
            raise SegmentDownloaderException(f"Can't load the cookies ({exc}).") from exc

    def __go_to_segment_page(self) -> None:
        """Navigate to the segment page.

        :exception SegmentDownloaderException: If the segment page can't be retrieved"""
        try:
            self.driver.get(f"https://www.strava.com/segments/{self.segment_id}")
            time.sleep(3)

            if self.completed_page > 0:
                self.__go_to_leaderboard_page()

                time.sleep(3)
        except WebDriverException as exc:
            raise SegmentDownloaderException(
                f"Can't retrieve the segment page "
                f"for segment {self.segment_id} ({exc.msg}).") from exc

    def __go_to_leaderboard_page(self) -> None:
        """Jump forward to the given leaderboard page.

        Note: Strava's website requires this rather strange methode to manipulate the next page
        button's link target. If we just call the URL it refers it won't work."""
        button = self.driver.find_element(By.LINK_TEXT, "→")
        old_href = button.get_attribute("href")

        left = old_href.find("page=") + 5
        right = old_href[left:].find("&")

        new_href = old_href[:left] + str(self.completed_page + 1) + old_href[left:][right:]

        self.driver.execute_script(
            f"document.getElementById(\"results\").getElementsByClassName(\"next_page\")"
            f"[0].children[0].setAttribute('href', '{new_href}')"
        )
        button.click()

    def __read_table(self) -> LeaderBoardType:
        """Read the current page's result table.

        :return: A list of dictionaries with the leaderboard's current page's data

        :exception SegmentDownloaderException: If the table can't be read"""
        leaderboard_data: LeaderBoardType = []

        try:
            rows = self.driver.find_elements(By.XPATH, "//*[@id=\"results\"]/table/tbody/tr")
            heads = self.driver.find_elements(By.XPATH, "//*[@id=\"results\"]/table/thead/tr")

            if not rows[0].find_element(By.XPATH, ".//td[1]").text == "No results found":
                is_climb = heads[0].find_element(By.XPATH, ".//th[7]").text == "VAM"

                for row in rows:
                    name = row.find_element(By.XPATH, ".//td[2]").text

                    date = row.find_element(By.XPATH, ".//td[3]").text
                    speed = row.find_element(By.XPATH, ".//td[4]").text[:-5]

                    fifth_column = row.find_element(By.XPATH, ".//td[5]").text
                    hr = fifth_column[:-4] if fifth_column != "-" else None

                    sixth_column = row.find_element(By.XPATH, ".//td[6]").text
                    power = sixth_column[:-14] if sixth_column.endswith("Power Meter") else None

                    if is_climb:
                        vam = row.find_element(By.XPATH, ".//td[7]").text.replace(",", "")
                        time_to_finish = row.find_element(By.XPATH, ".//td[8]").text
                    else:
                        time_to_finish = row.find_element(By.XPATH, ".//td[7]").text
                        vam = None

                    leaderboard_data.append({
                        "Name": name,
                        "Date": date,
                        "Speed": speed,
                        "Heart rate": hr,
                        "Power": power,
                        "VAM": vam,
                        "Time": time_to_finish
                    })
        except WebDriverException as exc:
            raise SegmentDownloaderException(
                f"Can't read the leaderboard table ({exc.msg}).") from exc

        return leaderboard_data

    def __read_full_tables(self, filters: Dict[str, str]) -> None:
        """Read the full table

        :param filters: The filters to apply to the table

        :exception SegmentDownloaderException: If the table can't be read or
        the filters can't be applied"""
        sex: Optional[str] = filters["sex"] if "sex" in filters else None
        age: Optional[str] = filters["age"] if "age" in filters else None
        weight: Optional[str] = filters["weight"] if "weight" in filters else None

        try:
            self.__apply_filters(filters)
        except WebDriverException as exc:
            raise SegmentDownloaderException(f"Can't apply the filters ({exc.msg}).") from exc

        while True:
            try:
                current_page = self.__read_table()

                self.leaderboard_data[(sex, age, weight)].extend(current_page)

                self.completed_page += 1

                self.driver.find_element(By.LINK_TEXT, "→").click()
                time.sleep(5)
            except NoSuchElementException:
                break
            except WebDriverException as exc:
                raise SegmentDownloaderException(
                    f"Can't navigate to the next page ({exc.msg}).") from exc

    def __apply_filters(self, filters: Dict[str, str]) -> None:
        """Apply the filters to the leaderboard view."""
        if "age" in filters:
            self.driver.find_element(By.CSS_SELECTOR, "li:nth-child(11) .expand").click()
            time.sleep(3)
            self.driver.find_element(By.LINK_TEXT, filters["age"]).click()
            time.sleep(3)
        if "weight" in filters:
            self.driver.find_element(By.CSS_SELECTOR, "li:nth-child(10) .expand").click()
            time.sleep(3)
            self.driver.find_element(By.LINK_TEXT, filters["weight"]).click()
            time.sleep(3)
        if "sex" in filters:
            self.driver.find_element(By.CSS_SELECTOR,
                                     ".text-nowrap:nth-child(4) .btn").click()
            time.sleep(3)
            self.driver.find_element(By.LINK_TEXT, filters["sex"]).click()
            time.sleep(3)

    def __scrape_current_leaderboard(self, filters: Dict[str, str], phase_counter: int) -> None:
        """Scape the leaderboard and return the dictionary.

        :param filters: The filters to apply to the table
        :param phase_counter: The current phase
        :return: A list of dictionaries with the leaderboard data

        :exception SegmentDownloaderException: If the leaderboard can't be scraped"""
        if self.completed_phase < phase_counter:
            self.__go_to_segment_page()

            self.__read_full_tables(filters)

            self.completed_phase += 1
            self.completed_page = 0

    def scrape_leaderboard(self) -> None:
        """Scrape the leaderboard, add the categories and write the data to a CSV file.

        :exception SegmentDownloaderException: If the leaderboard can't be scraped or
        the data can't be written to a CSV file."""
        try:
            phase_counter: int = 1
            self.__scrape_current_leaderboard({}, phase_counter)
            phase_counter += 1

            for s in CATEGORIES_SEX:
                for a in CATEGORIES_AGE:
                    self.__scrape_current_leaderboard({"sex": s, "age": a}, phase_counter)
                    phase_counter += 1

            for s in CATEGORIES_SEX:
                for w in CATEGORIES_WEIGHT:
                    self.__scrape_current_leaderboard({"sex": s, "weight": w}, phase_counter)
                    phase_counter += 1

            self.__add_attributes()

            self.__write_to_csv()
        except WebDriverException as exc:
            raise SegmentDownloaderException(f"Can't close the driver ({exc.msg}).") from exc

    def __add_attributes(self) -> None:
        """Add the attributes to the leaderboard data."""
        for i, entry in enumerate(self.leaderboard_data[(None, None, None)]):
            c_s: Optional[str] = None
            c_w: Optional[str] = None
            c_a: Optional[str] = None

            for s in CATEGORIES_SEX:
                for a in CATEGORIES_AGE:
                    if entry in self.leaderboard_data[(s, a, None)]:
                        c_s = s
                        c_a = a
                        break

            for s in CATEGORIES_SEX:
                for w in CATEGORIES_WEIGHT:
                    if entry in self.leaderboard_data[(s, None, w)]:
                        c_s = s
                        c_w = w
                        break

            self.leaderboard_data[(None, None, None)][i]["Age group"] = c_a
            self.leaderboard_data[(None, None, None)][i]["Weight group"] = c_w
            self.leaderboard_data[(None, None, None)][i]["Sex"] = c_s
            self.leaderboard_data[(None, None, None)][i]["Position"] = str(i + 1)

    def __write_to_csv(self) -> None:
        """Write the data to a CSV file.

        :exception SegmentDownloaderException: If the data can't be written to a CSV file."""
        field_names: List[str] = ["Position", "Name", "Date", "Speed", "Heart rate", "Power",
                                  "VAM", "Time", "Sex", "Age group", "Weight group"]
        filename: str = f"leaderboard_{self.segment_id}.csv"

        try:
            with open(filename, "w", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=field_names)
                writer.writeheader()
                writer.writerows(self.leaderboard_data[(None, None, None)])
        except (IOError, csv.Error) as exc:
            raise SegmentDownloaderException(
                f"Can't write the leaderboard data to a CSV file ({exc})") from exc

    def save_state(self) -> None:
        """Save the current state of the SegmentDownloader object.

        :exception SegmentDownloaderException: If the state can't be saved."""
        try:
            with open(FILENAME_STATE, "wb") as file:
                pickle.dump(self, file)
        except (IOError, pickle.PickleError) as exc:
            raise SegmentDownloaderException(f"Can't save the state ({exc}).") from exc

    @staticmethod
    def load_state() -> "SegmentDownloader":
        """Load the state of the SegmentDownloader object.

        :return: The SegmentDownloader object

        :exception SegmentDownloaderException: If the state can't be loaded."""
        try:
            with open(FILENAME_STATE, "rb") as file:
                return pickle.load(file)
        except (IOError, pickle.PickleError) as exc:
            raise SegmentDownloaderException(f"Can't load the state ({exc}).") from exc


def main() -> None:
    """Main function to download the leaderboard data."""
    try:
        parser = argparse.ArgumentParser(description="Process a Strava segment.")
        parser.add_argument("segment_id", type=int, help="The segment ID (numerical value)")
        parser.add_argument("--resume", action="store_true",
                            help="Resume from the last saved state if available.")

        args = parser.parse_args()

        leaderboard: SegmentDownloader = SegmentDownloader.load_state() \
            if args.resume else SegmentDownloader(str(args.segment_id))

        try:
            leaderboard.scrape_leaderboard()
        except KeyboardInterrupt:
            leaderboard.save_state()
            sys.exit(0)
    except SegmentDownloaderException as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
