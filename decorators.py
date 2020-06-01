import logging

from requests import HTTPError

from settings import logger_config

logging.config.dictConfig(logger_config)
logger = logging.getLogger('app_logger')


def http_error_decorator(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except HTTPError as e:
            logger.debug(str(e))
    return wrapper
