BOT_NAME = 'proxy_pool'
SPIDER_MODULES = ['proxy_pool.spiders']
NEWSPIDER_MODULE = 'proxy_pool.spiders'

# js 解析 scrapy_splash
SPLASH_URL = 'http://127.0.0.1:8050'

# robots.txt rules
ROBOTSTXT_OBEY = False

# Redis
REDIS_HOST = "127.0.0.1"
# redis 端口
REDIS_PORT = 6379
# redis 密码
REDIS_PASSWORD = ""
# redis set key
REDIS_KEY = "proxies:ranking"
# redis 连接池最大连接量
REDIS_MAX_CONNECTION = 20
# REDIS SCORE 最大分数
MAX_SCORE = 10
# REDIS SCORE 最小分数
MIN_SCORE = 0
# REDIS SCORE 初始分数
INIT_SCORE = 9

# 中间件
DOWNLOADER_MIDDLEWARES = {
    # 'proxy_pool.middlewares.ProxyPollDownloaderMiddleware': 543,
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

# Configure item pipelines
ITEM_PIPELINES = {
    'proxy_pool.pipelines.ProxyPollPipeline': 300,
}

# 爬取器循环周期（分钟）
CRAWLER_RUN_CYCLE = 30
# 校验器循环周期（分钟）
VALIDATOR_RUN_CYCLE = 15
# 校验器测试网站，可以定向改为自己想爬取的网站，如新浪，知乎等
VALIDATOR_BASE_URL = "https://httpbin.org/get?show_env=1"
# 请求超时时间
REQUEST_TIMEOUT = 8