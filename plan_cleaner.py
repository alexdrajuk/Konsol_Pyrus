import time
import logging.config

from pyrus import PyrusAccount
import lib

import schedule
from settings import logger_config

logging.config.dictConfig(logger_config)
logger = logging.getLogger('app_logger')


def clear_plans():
    user_credentials = lib.fetch_users_credentials()
    for credentials in user_credentials:
        credentials = dict(credentials)
        try:
            account = PyrusAccount(credentials.get('email'), credentials.get('secret_key'))
            account.clear_plan_list()
        except Exception:
            logger.debug('Something went wrong during clear_plans', exc_info=True)


schedule.every().monday.at("23:00").do(clear_plans)
schedule.every().tuesday.at("23:00").do(clear_plans)
schedule.every().wednesday.at("23:00").do(clear_plans)
schedule.every().thursday.at("23:00").do(clear_plans)
schedule.every().friday.at("23:00").do(clear_plans)


if __name__ == '__main__':
    while True:
        schedule.run_pending()
        time.sleep(1)
