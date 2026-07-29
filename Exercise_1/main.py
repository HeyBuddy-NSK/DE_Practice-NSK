import zipfile
from pathlib import Path
from urllib.parse import urlparse

import requests
from utils import setup_logger

# setting logger
logger = setup_logger("S3_file_download")

def check_valid_url(url: str) -> bool:
    """Check whether a given string is a valid HTTP/HTTPS URL.

    Args:
        url: The URL string to validate.

    Returns:
        True if the URL appears to be a valid HTTP or HTTPS URL (has a scheme
        of 'http' or 'https' or a non-empty network location), otherwise False.

    """
    try:
        parsed_url = urlparse(url)
    except Exception as e:  # noqa: BLE001
        logger.info(f"URL {url} is not valid {e}")
        return False
    else:
        return parsed_url.scheme in ("http", "https") or parsed_url.netloc

def download_file(url: str, save_path: str = "downloads") -> Path | None:
    """Download a single file from the provided URL to a specified destination path.

    Prameters:
        url: Accepts the string value for url.
        save_path: Accepts the path to save in string format.

    Returns:
        boolean value true for download success and false for download fail.

    """
    # checking if the give url is valid or not.
    if not check_valid_url(url):
        logger.error(f"Given url {url} is invalid.")
        return False

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

        logger.info(f"File {file_name} downloaded successfully!.")
        return file_path

    except requests.exceptions.ConnectionError:
        logger.critical(
            "Connection Error: Failed to reach the server (DNS failure or down)."
        )

    except requests.exceptions.Timeout:
        logger.critical(
            "Request Time Out: Server took longer than expected to response."
        )

    except requests.exceptions.HTTPError as h_err:
        logger.exception(
            f"HTTP Error: {h_err.response.status_code} - Link might be broken or not found.."
        )

    except requests.exceptions.MissingSchema:
        logger.exception(f"Missing URL schema (e.g. missing 'http://) : {url}")

    except requests.exceptions.RequestException as req_err:
        logger.critical(f"An unexpected network error occured: {req_err}")

    except OSError as err:
        logger.critical(f"Disk/File Error: Could not save file to disk ({err})")

    return None


def file_unzip(file_path: str, save_path: str = "data") -> bool:
    """ """
    # getting file name
    file_name = Path(file_path).name
    # checking if file is zip or not
    if not zipfile.is_zipfile(file_path):
        logger.error(f"File {file_name} is not a zip file.")
        return False

    # creating directory for extraction
    current_dir = Path(__file__).resolve().parent
    extract_path = current_dir.joinpath(save_path)
    extract_path.mkdir(parents=True,exist_ok=True)

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

            logger.info(f"File {Path(file_name).name} Extracted!.")

        # deleting the downloaded zip after extracting
        logger.info("Deleting file...")
        file_path.unlink(missing_ok=True)
        logger.info("File Deleted..")
        return True

    except zipfile.BadZipFile:
        logger.exception(f"corrupted file: {file_name} is badly formatted or corrupted")

    except FileNotFoundError:
        logger.exception(f"Missing file: Could not locate {file_name}")

    except PermissionError:
        logger.exception(f"Permission denied: Do not have permission to write to {extract_path}")

    except OSError as os_err:
        logger.exception(f"OS/Disk error: during extraction : {os_err}")

    except Exception as e:
        logger.exception(f"unexpected error occured while unzipping {file_name}:{e}")

    return False
