import logging
import zipfile
from pathlib import Path
from urllib.parse import urlparse

import requests
from config import Config

# setting logger
logger = logging.getLogger(Config.LOGGER_NAME)

def check_valid_url(url: str) -> bool:
    """Check whether a given string is a valid HTTP/HTTPS URL.

    Parameters
    ----------
    url : str
        The URL string to validate.

    Returns
    -------
    bool
        True if the URL appears to be a valid HTTP or HTTPS URL (has a scheme
        of 'http' or 'https' or a non-empty network location), otherwise False.

    """
    try:
        parsed_url = urlparse(url)
    except Exception:
        logger.exception("URL %s is not valid", url)
        return False
    else:
        return parsed_url.scheme in ("http", "https") or parsed_url.netloc


def delete_file(file_path: Path | str) -> bool:
    """Delete a file at the specified path.

    Parameters
    ----------
    file_path : Path | str
        The path to the file to delete.

    Returns
    -------
    bool
        True if the file was successfully deleted, False if the file does not exist.

    """
    try:
        path = Path(file_path)
        path.unlink()
        logger.info("File %s deleted successfully.", path.name)

    except OSError:
        logger.exception("Error deleting file: %s", file_path)

    else:
        return True

    return False

def is_valid_member(zip_member_list: list) -> list:
    """Check if a member of a zip file is a valid file (not a directory).

    Parameters
    ----------
    zip_member_list : list
        A list of member names in the zip file.

    Returns
    -------
    list
        A list of valid file names from the zip file.

    """
    # keeping only valid files.
    valid_member_list = []

    logger.debug("Filtering valid members from zip member list.")
    for name in zip_member_list:
        # dividing zip member in parts
        name_parts = Path(name).parts

        # getting only csv and non hidden file.
        is_valid = any(
                        part.endswith(".csv") and not part.startswith(".")
                        for part in name_parts
                    )

        # updating the valid member list
        if is_valid:
            valid_member_list.append(name)

    return valid_member_list


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

    # creating download directories if they don't exist.
    download_path = Config.BASE_DIR.joinpath(save_path)
    download_path.mkdir(parents=True,exist_ok=True)
    logger.debug("Created directory %s for downloads.", download_path)

    # generating file name from the url and creating file path to save.
    file_name = Path(url).name
    file_path = download_path.joinpath(file_name)

    # getting expected csv path.
    expected_csv_path = download_path.joinpath(file_name.replace(".zip", ".csv"))

    if file_path.exists() or expected_csv_path.exists():
        logger.info("Target data for File %s already exists. Skipping download.",
                    file_name)
        return file_path

    try:
        # `stream=True` to stream chunks into memory instead of loading the full payload
        logger.info("Starting download for url: %s", url)
        with requests.get(url, stream=True, timeout=Config.TIMEOUT) as resp:
            resp.raise_for_status()

            with open(file_path, "wb") as save_file_object:
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


def file_unzip(file_path: Path, extract_path: Path = Path("downloads")) -> bool:
    """Unzip a zip file to a specified destination path.

    Parameters
    ----------
    file_path : Path
        The path to the zip file to extract.
    extract_path : Path, optional
        The directory path where the extracted files will be saved.
        Defaults to Path("data").

    Returns
    -------
    bool
        True if the zip file was extracted successfully, False otherwise.

    """
    # getting file name
    file_name = file_path.name


    # getting expected csv path.
    expected_csv_path = extract_path.joinpath(file_name.replace(".zip", ".csv"))

    # checking if the file is already extracted
    if expected_csv_path.exists():
        logger.info("File %s already extracted. Skipping extraction.", file_name)
        return True

    # checking if the file exists before attempting extraction
    if not file_path.exists():
        logger.error("File %s does not exist. Cannot extract.", file_name)
        return False

    # checking if file is zip or not
    if not zipfile.is_zipfile(file_path):
        logger.error("File %s is not a zip file.",file_name)
        return False

    # creating directory for extraction if it doesn't exist
    extract_path = Config.BASE_DIR.joinpath(extract_path)
    extract_path.mkdir(parents=True,exist_ok=True)
    logger.debug("created directory %s for extraction.", extract_path)

    # extracting the zip file

    try:
        logger.info("Starting extraction for file: %s", file_name)
        with zipfile.ZipFile(file_path, mode="r") as zip_file_object:

            # getting all file names from the zip file
            zip_member_list = zip_file_object.namelist()

            # filtering out only valid files (ignoring directories)
            valid_member_list = is_valid_member(zip_member_list)

            # starting extraction
            for member in valid_member_list:
                member_path = extract_path.joinpath(member)
                if member_path.exists():
                    logger.info("File %s already exists. Skipping extraction.", member)
                    continue
                zip_file_object.extract(member, path=extract_path)

            logger.info("File %s Extracted!.", file_name)

        # deleting the downloaded zip after extracting
        delete_file(file_path)

    except zipfile.BadZipFile:
        logger.exception("corrupted file: %s is badly formatted or corrupted",
                         file_name)

    except OSError:
        logger.exception("OS/Disk error: during extraction of %s", file_name)

    except Exception:
        logger.exception("unexpected error occured while unzipping %s", file_name)

    else:
        return True

    return False
