import logging


level = logging.INFO


logging.basicConfig(level=level, format='%(asctime)s | %(levelname)-8s | %(name)-20s | Line: %(lineno)-5d | %(message)s', datefmt='%d-%m-%Y | %H:%M:%s')

def logger(loggerName=None):
    logger = logging.getLogger(loggerName)
    logger.setLevel(level)
    return logger

