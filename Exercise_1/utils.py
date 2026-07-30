import datetime
import logging
from logging import getLogger
from pathlib import Path


def setup_logger(name: str = __name__, log_folder: str = "logs") -> logging.Logger:
    """Configure a logger that writes level messages to a dated file.

    Parameters
    ----------
    name : str
        Name of the logger and prefix for the log file.
    log_folder : str
        Directory where log files are stored.

    Returns
    -------
    logging.Logger: configured logger instance.

    """
    # getting current directory and creating log folder if it doesn't exist.
    current_dir = Path(__file__).resolve().parent
    base = current_dir.joinpath(log_folder)

    if not base.exists():
        base.mkdir(parents=True, exist_ok=True)

    # creating logger object for given name.
    logger = getLogger(name)

    # setting logger level to INFO
    logger.setLevel(logging.INFO)

    # creating dynamic log file name for daily basis
    current_date = datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y-%m-%d")
    log_file_name = f"{name}-{current_date}.log"

    # creating log file path by joining base log folder and file name.
    log_file_path = base.joinpath(log_file_name)

    # creating handler logger
    if not logger.handlers:
        formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S")

        # setting up file handler and format
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(formatter)

        # setting up stream handler for console
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        # attaching handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger
