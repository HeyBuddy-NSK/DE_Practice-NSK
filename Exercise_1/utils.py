import datetime
import logging
from logging import getLogger
from pathlib import Path


def setup_logger(name: str = __name__, log_folder: str = "logs") -> getLogger:
    """Configure a logger that writes level messages to a dated file.

    Name
    ----
        setup_logger

    Parameters
    ----------
        name: Name of the logger and prefix for the log file.
        log_folder: Directory where log files are stored.

    Returns
    -------
        Configured logger instance.

    """
    base = Path(log_folder)
    if not base.exists():
        base.mkdir(parents=True, exist_ok=True)

    logger = getLogger(name)

    # creating dynamic log file name
    current_date = datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y-%m-%d")
    log_file_name = f"{name}-{current_date}.log"
    log_file_path = base.joinpath(log_file_name)

    # adding log file name to logger configuration
    logging.basicConfig(filename=log_file_path, level=logging.INFO)
    return logger
