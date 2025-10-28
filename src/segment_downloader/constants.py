"""Constants for the segment downloader library.

Written by Dominik Rappaport, dominik@rappaport.at, 2024
"""

from typing import List

FILENAME_STATE = "state.pkl"
FILENAME_COOKIES = "cookies.pkl"

CATEGORIES_SEX: List[str] = ["Men", "Women"]
CATEGORIES_AGE: List[str] = [
    "19 and under",
    "20 to 24",
    "25 to 34",
    "35 to 44",
    "45 to 54",
    "55 to 64",
    "65 to 69",
    "70 to 74",
    "75+",
]
CATEGORIES_WEIGHT: List[str] = [
    "54 kg and under",
    "55 to 64 kg",
    "65 to 74 kg",
    "75 to 84 kg",
    "85 to 94 kg",
    "95 kg to 104 kg",
    "105 kg to 114 kg",
    "115 kg and over",
]
