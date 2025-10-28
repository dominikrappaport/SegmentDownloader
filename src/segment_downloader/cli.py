"""Command-line interface for the segment downloader.

Written by Dominik Rappaport, dominik@rappaport.at, 2024
"""

import argparse
import sys

from .downloader import SegmentDownloader
from .exceptions import SegmentDownloaderException


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

        args = parser.parse_args()

        leaderboard: SegmentDownloader = (
            SegmentDownloader.load_state()
            if args.resume
            else SegmentDownloader(str(args.segment_id))
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
