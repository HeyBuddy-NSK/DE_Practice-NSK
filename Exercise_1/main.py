
import requests
from urllib.parse import urlparse

from .utils import setup_logger


# setting logger
logger = setup_logger('S3_file_download')

def chekc_valid_url(url: str) -> bool:
    """Check whether a given string is a valid HTTP/HTTPS URL.

    Args:
        url: The URL string to validate.

    Returns:
        True if the URL appears to be a valid HTTP or HTTPS URL (has a scheme
        of 'http' or 'https' or a non-empty network location), otherwise False.

    """
    try:
        parsed_url = urlparse(url)
        return parsed_url.scheme in ("http", "https") or parsed_url.netloc
    except Exception as e:
        logger.info(f"URL {url} is not valid {e}")
        return False


def download_file(url: str, save_path: str) -> bool:
    """Download a single file from the provided URL to a specified destination path.

    Prameters:
        url: Accepts the string value for url.
        save_path: Accepts the path to save in string format.

    """
    try:
        # `stream=True` to stream chunks into memory instead of loading the full payload.
        with requests.get(url, stream=True, timeout=7) as resp:
            resp.raise_for_status()

            with open(save_path, "wb") as save_file_object:
                # Using iter_content() for keeping ram usage to minimal.
                save_file_object.write(
                       content for content in resp.iter_content(chunk_size=8192)
                    )

        logger.info(f"File from {url} downloaded successfully!.")
        return True

    except requests.exceptions.ConnectionError:
        logger.critical("Connection Error: Failed to reach the server (DNS failure or down).")
    except requests.exceptions.Timeout:
        logger.critical("Request Time Out: Server took longer than expected to response.")
    except requests.exceptions.HTTPError as h_err:
        logger.error(f"HTTP Error: {h_err.response.status_code} - Link might be broken or not found..")
    except requests.exceptions.MissingSchema:
        logger.error(f"Missing URL schema (e.g. missing 'http://) : {url}")
    except requests.exceptions.RequestException as req_err:
        logger.critical(f"An unexpected network error occured: {req_err}")
    except OSError as err:
        logger.critical(f"Disk/File Error: Could not save file to disk ({err})")

    return False
