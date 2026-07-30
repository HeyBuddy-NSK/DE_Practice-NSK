import zipfile
from pathlib import Path
from urllib.parse import urlparse

import requests
from utils import setup_logger

# setting logger
logger = setup_logger("S3_file_download")

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


def delete_file(file_path: str) -> bool:
    """Delete a file at the specified path.

    Parameters
    ----------
    file_path : str
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

def download_file(url: str, save_path: str = "downloads") -> Path | None:
    """Download a single file from the provided URL to a specified destination path.

    Parameters
    ----------
    url : str
        The URL of the file to download.
    save_path : str, optional
        The directory path where the downloaded file will be saved.
        Defaults to "downloads".

    Returns
    -------
    Path | None
        The path to the downloaded file if successful, None otherwise.

    """
    logger.info("Starting download for url: %s", url)

    # checking if the give url is valid or not.
    if not check_valid_url(url):
        logger.error("Given url %s is invalid.", url)
        return None

    # creating download directories.
    current_dir = Path(__file__).resolve().parent
    download_path = current_dir.joinpath(save_path)
    download_path.mkdir(parents=True,exist_ok=True)

    # generating file name from the url and creating file path to save.
    file_name = Path(url).name
    file_path = download_path.joinpath(file_name)

    try:
        # `stream=True` to stream chunks into memory instead of loading the full payload
        logger.info("Downloading file!...")
        with requests.get(url, stream=True, timeout=7) as resp:
            resp.raise_for_status()

            with open(file_path, "wb") as save_file_object:
                # Using iter_content() for keeping ram usage to minimal.
                for content in resp.iter_content(chunk_size=8192):
                    if content:
                        save_file_object.write(content)

        logger.info("File %s downloaded successfully!.", file_name)

    except requests.exceptions.RequestException as req_err:
        logger.critical("An unexpected error occured while downloading: %s", req_err)

    except OSError as err:
        logger.critical("Disk/File Error: Could not save file to disk (%s)", err)

    else:
        return file_path

    return None


def file_unzip(file_path: str, save_path: str = "data") -> bool:
    """Unzip a zip file to a specified destination path.

    Parameters
    ----------
    file_path : str
        The path to the zip file to extract.
    save_path : str, optional
        The directory path where the extracted files will be saved.
        Defaults to "data".

    Returns
    -------
    bool
        True if the zip file was extracted successfully, False otherwise.

    """
    logger.info("Starting extraction for file: %s", file_path)

    # getting file name
    file_name = Path(file_path).name

    # checking if file is zip or not
    if not zipfile.is_zipfile(file_path):
        logger.error("File %s is not a zip file.",file_name)
        return False

    # creating directory for extraction
    current_dir = Path(__file__).resolve().parent
    extract_path = current_dir.joinpath(save_path)
    extract_path.mkdir(parents=True,exist_ok=True)
    logger.info("created directory %s for extraction.", extract_path)

    try:
        with zipfile.ZipFile(file_path, mode="r") as zip_file_object:

            # getting all file names from the zip file
            zip_member_list = zip_file_object.namelist()

            # keeping only valid files.
            valid_member_list = []

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


            # starting extraction
            for member in valid_member_list:
                zip_file_object.extract(member, path=extract_path)

            logger.info("File %s Extracted!.", file_name)

        # deleting the downloaded zip after extracting
        delete_file(file_path)

    except zipfile.BadZipFile:
        logger.exception("corrupted file: %s is badly formatted or corrupted",
                         file_name)

    except OSError:
        logger.exception("OS/Disk error: during extraction : %s")

    except Exception:
        logger.exception("unexpected error occured while unzipping %s", file_name)

    else:
        return True

    return False
