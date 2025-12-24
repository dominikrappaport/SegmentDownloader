"""Command-line interface for the segment downloader.

Written by Dominik Rappaport, dominik@rappaport.at, 2024
"""

import argparse
import sys
from typing import List, Optional

from .constants import CATEGORIES_AGE, CATEGORIES_SEX, CATEGORIES_WEIGHT
from .downloader import SegmentDownloader
from .exceptions import SegmentDownloaderException


def validate_filter_values(
    filter_values: Optional[str], valid_categories: List[str], filter_name: str
) -> List[str]:
    """Validate that filter values are valid according to the allowed categories.

    :param filter_values: Comma-separated string of filter values
    :param valid_categories: List of valid category values
    :param filter_name: Name of the filter (for error messages)
    :return: List of validated filter values
    :raises SegmentDownloaderException: If any filter value is invalid
    """
    if not filter_values:
        return []

    values = [v.strip() for v in filter_values.split(",")]
    invalid_values = [v for v in values if v not in valid_categories]

    if invalid_values:
        raise SegmentDownloaderException(
            f"Invalid {filter_name} filter value(s): {', '.join(invalid_values)}. "
            f"Valid values are: {', '.join(valid_categories)}"
        )

    return values


def main() -> None:
    """Main function to download the leaderboard data."""
    try:
        parser = argparse.ArgumentParser(description="Process a Strava segment.")
        parser.add_argument(
            "segment_id", type=int, help="The segment ID (numerical value)"
        )
        parser.add_argument(
            "--resume",
            action="store_true",
            help="Resume from the last saved state if available.",
        )
        parser.add_argument(
            "--filter-sex",
            type=str,
            help=f"Filter by sex. Comma-separated values from: {', '.join(CATEGORIES_SEX)}",
        )
        parser.add_argument(
            "--filter-age",
            type=str,
            help=f"Filter by age group. Comma-separated values from: {', '.join(CATEGORIES_AGE)}",
        )
        parser.add_argument(
            "--filter-weight",
            type=str,
            help=f"Filter by weight group. Comma-separated values from: {', '.join(CATEGORIES_WEIGHT)}",
        )

        args = parser.parse_args()

        # Validate filter arguments
        sex_filters = validate_filter_values(args.filter_sex, CATEGORIES_SEX, "sex")
        age_filters = validate_filter_values(args.filter_age, CATEGORIES_AGE, "age")
        weight_filters = validate_filter_values(
            args.filter_weight, CATEGORIES_WEIGHT, "weight"
        )

        leaderboard: SegmentDownloader = (
            SegmentDownloader.load_state()
            if args.resume
            else SegmentDownloader(
                str(args.segment_id),
                sex_filters=sex_filters if sex_filters else None,
                age_filters=age_filters if age_filters else None,
                weight_filters=weight_filters if weight_filters else None,
            )
        )

        # Print filter information
        if sex_filters or age_filters or weight_filters:
            print(
                f"Applying filters - Sex: {sex_filters or 'all'}, "
                f"Age: {age_filters or 'all'}, Weight: {weight_filters or 'all'}"
            )

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
