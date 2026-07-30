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
        file_name = downloaded_file_path.name if downloaded_file_path else url

        # checking if the download was successful before attempting extraction
        if downloaded_file_path:
            logger.info("Download Successful for %s!", file_name)

            # attempting to extract the downloaded file
            if file_unzip(downloaded_file_path, Config.EXTRACT_PATH):
                logger.info("Extraction complete for %s!", file_name)

            else:
                logger.error("Extraction failed for %s.", file_name)

        else:
            logger.error("Download Failed for %s. Skipping extraction.", file_name)

    logger.info("Download and extraction process completed.")

def download_single_file() -> None:
    """Download and extract the first file from Config.DOWNLOAD_URI.

    This convenience function downloads the first URL listed in
    Config.DOWNLOAD_URI and attempts to extract it. Logging is used to
    report success or failure of download and extraction steps.
    """
    # downloading one file
    url = Config.DOWNLOAD_URI[0]
    download_file_path = download_file(url, Config.DOWNLOAD_PATH)

    if download_file_path:
        logger.info("Download Successful for %s!", url)

        if file_unzip(download_file_path, Config.EXTRACT_PATH):
            logger.info("Extraction complete for %s!", download_file_path)
    else:
        logger.error("Download Failed for %s.", url)

if __name__=="__main__":
    download_and_extract_files()
