import logging

# Level
level = logging.INFO
loggerName = "p-geo"

logging.basicConfig(level=level,
                    format='%(asctime)s | %(levelname)-8s | %(name)-20s | Line: %(lineno)-5d | %(message)s',
                    datefmt='%d-%m-%Y | %H:%M:%s')
logger = logging.getLogger(loggerName)
logger.setLevel(level)