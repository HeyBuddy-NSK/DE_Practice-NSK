"""Utility helpers for ingestion related file operations."""

import logging
import zipfile
from pathlib import Path
from urllib.parse import urlparse

from src.config import Config

logger = logging.getLogger(__name__)

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
        result =  parsed_url.scheme in ("http", "https") or parsed_url.netloc

    except Exception:
        logger.exception("URL %s is not valid", url)
    else:
        return bool(result)

    return False


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
        A list of valid csv file names from the zip file.

    """
    # checking if the input is a list and not None
    if zip_member_list is None or not isinstance(zip_member_list, list):
        logger.warning("Invalid input: Expected a list of zip members, got: %s",
                       type(zip_member_list).__name__)
        return []

    # checking if the list is empty
    if len(zip_member_list) == 0:
        logger.warning("Empty zip member list provided.")
        return []

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
    file_path = Path(file_path)
    file_name = file_path.name

    # getting expected csv path.
    expected_csv_path = extract_path.joinpath(file_name.replace(".zip", ".csv"))

    # checking if the file is already extracted
    if expected_csv_path.exists():
        logger.info("File %s already extracted. Skipping extraction.", file_name)
        return True

    # checking if the file exists before attempting extraction
    if not file_path.exists():
        logger.warning("File %s does not exist. Cannot extract.", file_name)
        return False

    # checking if the file path is a valid zip file
    if ( file_path.is_dir() or
        not file_path.name.endswith(".zip") or
        not zipfile.is_zipfile(file_path) ):

        logger.warning(
            "Invalid file path provided, or File does not exist, got: %s",
            file_path )

        return False

    # creates directory for extraction if it doesn't exist
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
