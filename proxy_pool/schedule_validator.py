import schedule
from proxy_pool.settings import CRAWLER_RUN_CYCLE, VALIDATOR_RUN_CYCLE, VALIDATOR_BASE_URL
import os
import time
from proxy_pool.logger import logger
from proxy_pool.database import RedisClient
from proxy_pool.validator import validator


def crawler():
    os.system("scrapy crawl crawler")


def validate():
    redis = RedisClient()
    logger.info("Validator working...")
    logger.info("Validator website is {}".format(VALIDATOR_BASE_URL))
    validator.main(redis.all_proxies())


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


