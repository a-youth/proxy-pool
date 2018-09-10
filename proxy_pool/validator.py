# -*- coding: utf-8 -*-
import time, asyncio, aiohttp
import socket
import requests
from .logger import logger
from .database import RedisClient
from .settings import VALIDATOR_BASE_URL, REQUEST_TIMEOUT


def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


class Validator:

    def __init__(self):
        self.timeout = REQUEST_TIMEOUT or 8
        concurrency = 100
        self.concurrency = concurrency
        """
            TCPConnector维持链接池，限制并行连接的总量，当池满了，有请求退出再加入新请求
            ClientSession调用TCPConnector构造连接，Session可以共用
            Semaphore限制同时请求构造连接的数量，Semphore充足时，总时间与timeout差不多
        """
        self.sem = asyncio.Semaphore(concurrency)
        self.conn = aiohttp.TCPConnector(ssl=False,
                                         limit=concurrency,
                                         use_dns_cache=True)
        self.redis = RedisClient()

    async def validate_douban_movie(self, session, proxy):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6,la;q=0.5',
            'connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Host': 'movie.douban.com',
            "Referer": "https://www.douban.com/",
            'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
        }
        async with session.get(url="https://movie.douban.com/subject/26861685/?from=showing",
                               proxy=proxy,
                               timeout=self.timeout,
                               headers=headers) as response:
            if response.status != 200:
                logger.info("{} douban error".format(proxy))
                return False
            else:
                logger.info("{} douban access".format(proxy))
                return True

    def validate_proxy(self, proxies):
        # try:
        #     # 超过10秒就放弃

        response = requests.get(VALIDATOR_BASE_URL, proxies=proxies, timeout=10, verify=True)
        if response.status_code == 200:
            httpbin = response.json()
            origin = httpbin.get('origin', None)
            proxy = proxies.get('http') or proxies.get('https')
            print(proxy)
            print(origin)
            if proxy.find(origin) >= 0:
                print("高匿")
                return True
            else:
                print("透明")
                return False

        # except Exception as err:
        #     print(proxies, "失效", err)
        #     return False

    async def validate_anonymous(self, session, proxy):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6,la;q=0.5',
            'connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Host': 'httpbin.org',
            'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
        }

        async with session.get(url=VALIDATOR_BASE_URL,
                               proxy=proxy,
                               timeout=self.timeout,
                               headers=headers) as response:
            if response.status == 200:
                httpbin = await response.json()
                origin = httpbin.get('origin', None)
                if proxy.find(origin) >= 0:
                    logger.info("{} 高匿".format(proxy))
                    return True
                else:
                    logger.info("{} 普匿".format(proxy))
                    return False

    async def proxy_connect(self, proxy, session):
        async with self.sem:
            try:
                anonymous_res = await self.validate_anonymous(session, proxy)
                if anonymous_res:
                    douban_res = await self.validate_douban_movie(session, proxy)
                    if douban_res:
                        # douban access
                        self.redis.add_proxy(proxy=proxy, score=1)
                        return
                self.redis.reduce_proxy_score(proxy)
            except Exception as error:
                logger.info("{} 验证失败 {}".format(proxy, error))
                self.redis.reduce_proxy_score(proxy)
                return False

    async def init(self, loop, proxies):
        async with aiohttp.ClientSession(connector=self.conn, loop=loop) as session:
            tasks = []
            for proxy in proxies:
                if isinstance(proxy, bytes):
                    proxy = proxy.decode("utf8")
                tasks.append(self.proxy_connect(proxy=proxy, session=session))
            await asyncio.wait(tasks)

    def main(self, proxies):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.init(loop=loop, proxies=proxies))


validator = Validator()

if __name__ == "__main__":
    validator.main(proxies=["https://183.154.215.78:9000"])
