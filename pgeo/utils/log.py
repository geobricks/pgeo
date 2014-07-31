import logging
from pgeo.config.settings import settings

level = settings["logging"]["level"]
format = settings["logging"]["format"]
datefmt = settings["logging"]["datefmt"]
logging.basicConfig(level=level,
                    format=format,
                    datefmt=datefmt)


def logger(loggerName=None):
    logger = logging.getLogger(loggerName)
    logger.setLevel(level)
    return logger


