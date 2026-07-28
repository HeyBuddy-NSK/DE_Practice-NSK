import datetime
import logging
import os
from logging import getLogger


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
    if not os.path.exists(log_folder):
        os.makedirs(log_folder, exist_ok=True)

    logger = getLogger(name)

    # creating dynamic log file name
    current_date = datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y-%m-%d")
    log_file_name = f"{name}-{current_date}.log"
    log_file_path = os.path.join(log_folder, log_file_name)

    # adding log file name to logger configuration
    logging.basicConfig(filename=log_file_path, level=logging.INFO)
    return logger
