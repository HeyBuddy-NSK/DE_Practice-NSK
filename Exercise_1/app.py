from config import Config
from data_ingestion import download_file, file_unzip
from utils import setup_logger

# Setting up logger
logger = setup_logger(Config.LOGGER_NAME, log_folder="logs")

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

def download_single_file() -> None:
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

if __name__=="__main__":
    download_and_extract_files()
