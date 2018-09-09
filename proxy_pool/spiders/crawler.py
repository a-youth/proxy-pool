# -*- coding: utf-8 -*-
import scrapy
from proxy_pool.items import ProxyIpItem
import re
from scrapy_splash import SplashRequest


class CrawlerSpider(scrapy.Spider):
    name = 'crawler'

    data_5u_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6,la;q=0.5",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Host": "www.data5u.com",
        "Referer": "http://www.data5u.com/free/country/%E4%B8%AD%E5%9B%BD/index.html",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/68.0.3440.106 Safari/537.36"
    }

    xicidaili_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6,la;q=0.5",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Cookie": "_free_proxy_session=BAh7B0kiD3Nlc3Npb25faWQGOgZFVEkiJTJjNDcxNmJmNmI0YzViZDA1NTlkOTNlNWIyMTAz"
                  "ODJlBjsAVEkiEF9jc3JmX3Rva2VuBjsARkkiMXFVRnNDVUJqam11L010eWVLYUJHTVZQbkxXQXV2ZUNuSXJjS1NMZTJXVn"
                  "M9BjsARg%3D%3D--11dee86176d8b5744e050301d8f612e0df6adcf1; Hm_lvt_0cf76c77469e965d2957f0553e6ecf59="
                  "1536225422,1536245878; Hm_lpvt_0cf76c77469e965d2957f0553e6ecf59=1536246012",
        "Host": "www.xicidaili.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/68.0.3440.106 Safari/537.36"
    }

    proxy_db_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6,la;q=0.5",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Cookie": "_ga=GA1.2.565120959.1536231204; _gid=GA1.2.588290526.1536321493",
        "Host": "proxydb.net",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/68.0.3440.106 Safari/537.36"
    }

    def start_requests(self):
        yield scrapy.Request("http://www.66ip.cn/nmtq.php?getnum=100&isp=0&anonymoustype=0&area=0&proxytype=1&api=66ip",
                             callback=self.parse_66ip)
        yield scrapy.Request("http://www.data5u.com/free/type/https/index.html",
                             headers=self.data_5u_headers,
                             callback=self.parse_data5u)
        yield scrapy.Request("http://ip.seofangfa.com/",
                             callback=self.parse_seofangfa)
        for page in range(1, 5):
            yield scrapy.Request("http://www.xicidaili.com/wn/{}".format(page),
                                 headers=self.xicidaili_headers,
                                 callback=self.parse_xicidaili)
        for page in range(0, 5):
            yield SplashRequest(url="http://proxydb.net/?protocol=https&country=&offset={}".format(page * 15),
                                headers=self.proxy_db_headers,
                                callback=self.parse_proxydb)

        yield SplashRequest(url="http://www.site-digger.com/html/articles/20110516/proxieslist.html",
                            callback=self.parse_digger)

    def parse_66ip(self, response):
        pattern = "\d+\.\d+.\d+\.\d+:\d+"
        html = response.body.decode(response.encoding)
        for proxy in re.findall(pattern, html):
            item = ProxyIpItem()
            item['proxy'] = proxy
            yield item

    def parse_data5u(self, response):
        for ip_xpath in response.xpath('//ul[@class="l2"]//a/ancestor::ul[@class="l2"]'):
            item = ProxyIpItem()
            ip = ip_xpath.xpath('./span[1]/li/text()').extract_first()
            port = ip_xpath.xpath('./span[2]/li/text()').extract_first()
            if ip and port:
                item['proxy'] = "{}:{}".format(ip, port)
                yield item

    def parse_xicidaili(self, response):
        for ip_xpath in response.xpath('//table//tr'):
            item = ProxyIpItem()
            ip = ip_xpath.xpath('./td[2]/text()').extract_first()
            port = ip_xpath.xpath('./td[3]/text()').extract_first()
            if ip and port:
                item['proxy'] = "{}:{}".format(ip, port)
                yield item

    def parse_seofangfa(self, response):
        for ip_xpath in response.xpath('//tbody/tr'):
            item = ProxyIpItem()
            ip = ip_xpath.xpath('./td[1]/text()').extract_first()
            port = ip_xpath.xpath('./td[2]/text()').extract_first()
            if ip and port:
                item['proxy'] = "{}:{}".format(ip, port)
                yield item

    def parse_proxydb(self, response):
        # print(response.body.decode(response.encoding))
        for ip_xpath in response.xpath('//tbody/tr'):
            item = ProxyIpItem()
            ip_port = ip_xpath.xpath('.//a/text()').extract_first() or ''
            if ip_port.strip():
                item['proxy'] = ip_port
                yield item

    def parse_digger(self, response):
        # print(response.body.decode(response.encoding))
        for ip_xpath in response.xpath('//table[@id="proxies_table"]/tbody/tr'):
            item = ProxyIpItem()
            ip_port = ip_xpath.xpath('./td[1]/text()').extract_first() or ''
            if ip_port:
                item['proxy'] = ip_port.strip()
                yield item
