import logging
from pgeo.config.settings import settings

level = settings["logging"]["level"]
format = settings["logging"]["format"]
logging.basicConfig(level=level, format=format)


def logger(loggerName=None):
    logger = logging.getLogger(loggerName)
    logger.setLevel(level)
    return logger


