"""Application entry point for downloading and extracting files.

This script serves as the main entry point for the application, orchestrating
"""
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

from src import Config, download_all_async, download_file, file_unzip, setup_logger

# Setting up logger
setup_logger(log_folder="logs")

# getting logger instance for this module
logger = logging.getLogger(__name__)

def download_and_extract_files() -> None:
    """Download and extract files from the specified URLs in the Config class."""
    logger.info("Starting the download and extraction process for files.")

    # starting multiple file download and extraction
    for url in Config.DOWNLOAD_URI:

        # downloading file from the given url
        downloaded_file_path = download_file(url, Config.DOWNLOAD_PATH)

        # checking if the download was successful before attempting extraction
        if downloaded_file_path:
            # attempting to extract the downloaded file
            file_unzip(downloaded_file_path, Config.EXTRACT_PATH)

    logger.info("Download and extraction process completed.")

def download_and_extract_single_file() -> None:
    """Download and extract the first file from Config.DOWNLOAD_URI.

    This convenience function downloads the first URL listed in
    Config.DOWNLOAD_URI and attempts to extract it. Logging is used to
    report success or failure of download and extraction steps.
    """
    # downloading one file
    url = Config.DOWNLOAD_URI[0]

    # downloading the file from the given url
    download_file_path = download_file(url, Config.DOWNLOAD_PATH)

    if download_file_path:
        file_unzip(download_file_path, Config.EXTRACT_PATH)
    logger.info("Single file download and extraction process completed.")

def download_and_extract_async() -> None:
    """Download and extract files asynchronously."""
    # getting constants from config
    urls = Config.DOWNLOAD_URI
    sem = Config.SEMAPHORE
    save_path = Config.DOWNLOAD_PATH
    extract_path = Config.EXTRACT_PATH

    # downloading files
    downloaded_file_paths = asyncio.run(download_all_async(urls,save_path,sem))

    # starting extraction
    if downloaded_file_paths:
        logger.info("Starting file extraction..")

        with ThreadPoolExecutor(max_workers = Config.MAX_WORKERS) as executor:
            for path in downloaded_file_paths:
                executor.submit(file_unzip, path, extract_path)

        logger.info("All files extracted successfully.")
    else:
        logger.warning("No files to extract.")


if __name__=="__main__":
    download_and_extract_async()
