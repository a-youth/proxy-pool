import asyncio
from proxy_pool.database import RedisClient
import time
import aiohttp
from proxy_pool.validator import Validator

now = lambda: time.time()

redis = RedisClient()


async def do_some_work(x):
    print('Waiting: ', x)

    await asyncio.sleep(x)
    return 'Done after {}s'.format(x)


async def validate_anonymous(session, proxy):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6,la;q=0.5',
        'connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Host': 'httpbin.org',
        'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }

    async with session.get(url="https://httpbin.org/get?show_env=1",
                           proxy=proxy,
                           timeout=5,
                           headers=headers) as response:
        if response.status == 200:
            httpbin = await response.json()
            origin = httpbin.get('origin', None)
            if proxy.find(origin):
                print("{} 高匿".format(proxy))
                return True
            else:
                print("{} 普匿".format(proxy))
                return False


async def init(loop, proxies):
    conn = aiohttp.TCPConnector(verify_ssl=False,
                                limit=100,
                                use_dns_cache=True)
    async with aiohttp.ClientSession(loop=loop, connector=conn) as session:
        tasks = []
        for proxy in proxies:
            if isinstance(proxy, bytes):
                proxy = proxy.decode("utf8")
            tasks.append(validate_anonymous(session=session, proxy=proxy))
        await asyncio.wait(tasks)


if __name__ == '__main__':
    start = now()
    # proxies = redis.all_proxies()
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(init(loop=loop, proxies=proxies))

    # client = redis.redis
    # key = 'demo'
    # # redis.add_proxy(key, 1)
    # redis.reduce_proxy_score(key)
    validator = Validator()
    validator.main(['http://103.103.182.56:59567'])

    print('TIME: ', now() - start)
