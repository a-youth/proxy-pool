import schedule
from proxy_pool.settings import CRAWLER_RUN_CYCLE, VALIDATOR_RUN_CYCLE, VALIDATOR_BASE_URL
import os
import time
from proxy_pool.logger import logger
from proxy_pool.database import RedisClient
from proxy_pool.validator import Validator


def crawler():
    os.system("scrapy crawl crawler")


def validate():
    redis = RedisClient()
    all_proxies = redis.all_proxies()
    validator = Validator()
    logger.info("Validator working...")
    logger.info("Validator website is {}".format(VALIDATOR_BASE_URL))
    if all_proxies:
        validator.main(redis.all_proxies())
    else:
        logger.info("empty proxies")


def run_schedule():
    # 启动收集器
    schedule.every(CRAWLER_RUN_CYCLE).minutes.do(crawler).run()
    # 启动验证器
    schedule.every(VALIDATOR_RUN_CYCLE).minutes.do(validate).run()

    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            logger.info("You have canceled all jobs")
            return


