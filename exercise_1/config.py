"""Configuration constants for download URIs and local paths."""

from pathlib import Path


class Config:
    """Configuration constants for download URIs and local paths.

    Attributes:
        DOWNLOAD_URI (tuple): Remote ZIP file URLs to download.
        EXTRACT_PATH (str): Local path where ZIP contents are extracted.
        DOWNLOAD_PATH (str): Local path where ZIP files are stored.

    """

    # defining download URIs for Divvy trip data
    DOWNLOAD_URI = (
        "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2018_Q4.zip",
        "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q1.zip",
        "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q2.zip",
        "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q3.zip",
        "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q4.zip",
        "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2020_Q1.zip",
        "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2220_Q1.zip",
    )

    # defining base directory and download/extract paths
    BASE_DIR = Path(__file__).resolve().parent
    EXTRACT_PATH = DOWNLOAD_PATH = BASE_DIR.joinpath("downloads")

    # defining timeout for download requests
    TIMEOUT = 7  # seconds
