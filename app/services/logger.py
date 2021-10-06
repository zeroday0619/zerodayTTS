import functools
import logging
import os

from rich.logging import RichHandler


def generate_log():
    """
    Create a logger object
    :return: Logger object.
    """
    log_format = "%(levelname)s %(asctime)s %(funcName)20s %(message)s"

    # Create a logger and set the level.
    for i in ["ZerodayTTS", "ffmpeg", "asyncio", "subprocess", "discord"]:
        logger = logging.getLogger(i)
    logger.setLevel(logging.INFO)
    logger.handlers = [RichHandler(rich_tracebacks=True, show_time=True)]

    log_dir = os.path.expanduser("~/log")
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)

    LOG_PATH = os.path.expanduser("~/log/WindowsInsiderBot.log")
    file_handler = logging.FileHandler(filename=LOG_PATH)

    formatter = logging.Formatter(log_format)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger


def LogDecorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = generate_log()

        try:
            logger.debug("{0} : {1} - {2} - {3}".format(func.__name__, *args, kwargs))
            result = func(*args, **kwargs)
            logger.debug(result)
            return result
        except Exception:
            issue = "exception in " + func.__name__ + "\n"
            logger.exception(issue)

    return wrapper
