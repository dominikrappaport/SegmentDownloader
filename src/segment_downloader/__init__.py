"""Segment Downloader library.

Download the full leaderboard for a given Strava segment including the categorical
information and write the results in a CSV file.

Written by Dominik Rappaport, dominik@rappaport.at, 2024
"""

from .authenticate import authenticate
from .constants import (
    CATEGORIES_AGE,
    CATEGORIES_SEX,
    CATEGORIES_WEIGHT,
    FILENAME_COOKIES,
    FILENAME_STATE,
)
from .downloader import SegmentDownloader
from .exceptions import SegmentDownloaderException

__all__ = [
    "authenticate",
    "SegmentDownloader",
    "SegmentDownloaderException",
    "FILENAME_STATE",
    "FILENAME_COOKIES",
    "CATEGORIES_SEX",
    "CATEGORIES_AGE",
    "CATEGORIES_WEIGHT",
]

__version__ = "0.1.3"
__author__ = "Dominik Rappaport"
__email__ = "dominik@rappaport.at"
__license__ = "MIT"
__url__ = "https://github.com/dominikrappaport/SegmentDownloader"
__description__ = "Allows to fully download a Strava leaderboard and saves it into a CSV file for further statistical analysis"
__keywords__ = "download strava leaderboards screen-scraping"
__package_name__ = "segment_downloader"
__readme_name__ = "README.md"
