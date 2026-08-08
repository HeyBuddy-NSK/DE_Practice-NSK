"""async_data_ingestion.

Asynchronous utilities to download files from URLs using aiohttp.

This module provides functions to download a single file or multiple files
concurrently with controlled concurrency limits.
"""

import asyncio
import logging
from pathlib import Path

import aiofiles
import aiofiles.os as aios
import aiohttp
from src.config import Config
from src.ingestion_helper import check_valid_url

logger = logging.getLogger(__name__)


async def download_file_async(
        session: aiohttp.ClientSession,
        save_path: Path,
        url: str,
        sem: asyncio.Semaphore)-> Path | None:
    """Fetch data from a given URL using an aiohttp session.

    Parameters
    ----------
    session : aiohttp.ClientSession
        The aiohttp session to use for making the request.
    save_path : pathlib.Path
        The path to the file where the fetched data will be saved.
    url : str
        The URL to fetch data from.
    sem : asyncio.Semaphore
        The semaphore number to control concurrency.

    Returns
    -------
    pathlib.Path | None
        The path to the saved file if the request was successful, None otherwise.

    """
    # checking if the url is valid before making the request
    if not check_valid_url(url):
        logger.error("Invalid URL: %s", url)
        return None

    async with sem:
        # creating path for download if user gives relative path
        download_path = Config.BASE_DIR.joinpath(save_path)

        # generating file path from the url and creating file path to save.
        file_name = Path(url).name
        file_path = download_path.joinpath(file_name)

        expected_csv_path = download_path.joinpath(file_name.replace(".zip",".csv"))

        try:
            # checking if file already exists
            expected_csv = await aios.path.exists(expected_csv_path)
            file = await aios.path.isfile(file_path)

            if file or expected_csv:
                logger.info(
                    "Target Data for File %s already exists, skipping the download",
                    file_name)
                return file_path

            # creating download directory if it doesnt exist
            await aios.makedirs(download_path,exist_ok=True)

            logger.info("Starting File donwload for : %s",file_name)
            # making an asynchronous GET request to the specified URL
            async with session.get(url) as resp:
                resp.raise_for_status()

                # writing the response content to the specified file in chunks
                async with aiofiles.open(file_path,"wb") as save_file_object:
                    async for content in resp.content.iter_chunked(8192):
                        if content:
                            await save_file_object.write(content)

            logger.info("File %s downloaded successfully!.", file_name)

        except aiohttp.ClientError:
            logger.exception(
                "An unexpected error occurred while downloading from %s", url)
        except asyncio.TimeoutError:
            logger.exception("Request timed out while downloading from %s", url)
        except OSError:
            logger.exception("Disk/File Error: Could not save file to disk")
        except Exception:
            logger.exception("Failed to fetch data from %s", url)

        else:
            return file_path
        return None

async def download_all_async(
        urls: tuple,
        save_path: Path,
        sem: int = 3) -> list:
    """Download multiple files asynchronously given a list of URLs.

    Parameters
    ----------
    urls : tuple
        Tuple of URL strings to download.
    save_path : pathlib.Path
        Directory path where downloaded files will be saved.
    sem : asyncio.Semaphore
        Concurrency limit (either an asyncio.Semaphore or an integer
        used to construct one).

    Returns
    -------
    result : List
        This coroutine schedules downloads and returns
        list of downloaded file paths once all are complete.

    """
    # created semaphore object for controled concurrency
    sem = asyncio.Semaphore(sem)

    logger.info("Starting async download..")

    # starting aiohttp client session.
    async with aiohttp.ClientSession() as session:
        tasks = []

        for url in urls:
            # creating coroutine for asyncio tasks
            coroutine = download_file_async(session,save_path,url,sem)
            tasks.append(coroutine)

        # awaiting for tasks to finish.
        result = await asyncio.gather(*tasks)
    logger.info("async download complete..")
    return result
