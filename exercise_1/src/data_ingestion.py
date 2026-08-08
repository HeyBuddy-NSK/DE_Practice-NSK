"""Data ingestion utilities for Exercise 1.

This module provides URL validation, file deletion, archive extraction, file downloading,
and member validation functions to support the data ingestion workflow.
"""

import logging
from pathlib import Path

import requests
from src.config import Config
from src.ingestion_helper import check_valid_url

# setting logger
logger = logging.getLogger(__name__)


def download_file(url: str, save_path: Path = Path("downloads")) -> Path | None:
    """Download a single file from the provided URL to a specified destination path.

    Parameters
    ----------
    url : str
        The URL of the file to download.
    save_path : Path | None
        The directory path where the downloaded file will be saved.
        Defaults to Path("downloads").

    Returns
    -------
    Path | None
        The path to the downloaded file if successful, None otherwise.

    """
    # checking if the give url is valid or not.
    if not check_valid_url(url):
        logger.error("Given url %s is invalid.", url)
        return None

    # creating path for download if user gives relative path.
    download_path = Config.BASE_DIR.joinpath(save_path)

    # generating file name from the url and creating file path to save.
    file_name = Path(url).name
    file_path = download_path.joinpath(file_name)

    # getting expected csv path.
    expected_csv_path = download_path.joinpath(file_name.replace(".zip", ".csv"))


    try:
        # checking if the file already exists to avoid re-downloading
        if file_path.is_file() or expected_csv_path.exists():
            logger.info("Target data for File %s already exists. Skipping download.",
                        file_name)
            return file_path

        # creating directory for download if it doesn't exist
        download_path.mkdir(parents=True, exist_ok=True)
        logger.debug("Created directory %s for downloads.", download_path)

        # `stream=True` to stream chunks into memory instead of loading the full payload
        logger.info("Starting download for url: %s", url)
        with requests.get(url, stream=True, timeout=Config.TIMEOUT) as resp:
            resp.raise_for_status()

            # with open(file_path, "wb") as save_file_object:

            # using Path.open() to open the file in binary write mode
            # as it is the best way when already have a Path object.
            with file_path.open("wb") as save_file_object:
                # Using iter_content() for keeping ram usage to minimal.
                for content in resp.iter_content(chunk_size=8192):
                    if content:
                        save_file_object.write(content)

        logger.info("File %s downloaded successfully!.", file_name)

    except requests.exceptions.RequestException:
        logger.exception("An unexpected error occured while downloading:")

    except OSError:
        logger.exception("Disk/File Error: Could not save file to disk")

    else:
        return file_path

    logger.error("Download failed for url: %s", url)
    return None
