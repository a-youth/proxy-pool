# -*- coding: utf-8 -*-
import scrapy
from proxy_pool.items import ProxyIpItem
from scrapy_splash import SplashRequest
import re
import json


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

    ip3366_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6,la;q=0.5",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Host": "www.ip3366.net",
        "Pragma": "no-cache",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/68.0.3440.106 Safari/537.36"
    }

    def start_requests(self):
        for page in range(1, 10):
            yield scrapy.Request("https://www.cool-proxy.net/proxies?sort=score&direction=desc&page={}".format(page),
                                 callback=self.parse_cool_proxy)
        # for page in range(1, 20):
        #     if page < 9:
        #         page = '0{}'.format(page)
        #     yield SplashRequest("http://nntime.com/proxy-list-{}.htm".format(page),
        #                         callback=self.parse_nntime)
        yield scrapy.Request("http://www.xiaohexia.cn/getip.php?num=100&protocol=https&format=json",
                             callback=self.parse_xiaohexia)
        yield scrapy.Request("https://31f.cn/https-proxy/",
                             callback=self.parse_31f)
        yield scrapy.Request("https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1",
                             callback=self.parse_proxylistplus)
        yield scrapy.Request("http://www.66ip.cn/nmtq.php?getnum=100&isp=0&anonymoustype=0&area=0&proxytype=1&api=66ip",
                             callback=self.parse_66ip)
        yield scrapy.Request("http://www.data5u.com/free/type/https/index.html",
                             headers=self.data_5u_headers,
                             callback=self.parse_data5u)
        yield scrapy.Request("http://ip.seofangfa.com/",
                             callback=self.parse_seofangfa)
        for page in range(1, 15):
            yield scrapy.Request("http://www.xicidaili.com/wn/{}".format(page),
                                 headers=self.xicidaili_headers,
                                 callback=self.parse_xicidaili)
        # for page in range(0, 15):
        #     yield SplashRequest(url="http://proxydb.net/?protocol=https&country=&offset={}".format(page * 15),
        #                         headers=self.proxy_db_headers,
        #                         callback=self.parse_proxydb)
        #
        # yield SplashRequest(url="http://www.site-digger.com/html/articles/20110516/proxieslist.html",
        #                     callback=self.parse_digger)

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

    def parse_proxylistplus(self, response):
        # print(response.body.decode(response.encoding))
        # print(response.xpath('//table[2]/tbody/tr[contains(@class,"cells")]/td[2]/text()').extract_first())

        for tr in response.xpath('//table[contains(@class,"bg")]//tr[contains(@class,"cells")]'):
            item = ProxyIpItem()
            ip = tr.xpath('./td[2]/text()').extract_first() or ''
            port = tr.xpath('./td[3]/text()').extract_first() or ''
            # protocol = tr.xpath('./td[7]/text()').extract_first() or ''
            if ip and port:
                item['proxy'] = "{}:{}".format(ip, port)
                yield item

    def parse_31f(self, response):
        # print(response.body.decode(response.encoding))
        # print(response.xpath('//table[2]/tbody/tr[contains(@class,"cells")]/td[2]/text()').extract_first())
        for tr in response.xpath('//table[contains(@class, "table-striped")]//tr'):
            item = ProxyIpItem()
            ip = tr.xpath('./td[2]/text()').extract_first() or ''
            port = tr.xpath('./td[3]/text()').extract_first() or ''
            # protocol = tr.xpath('./td[7]/text()').extract_first() or ''
            if ip and port:
                item['proxy'] = "{}:{}".format(ip, port)
                yield item

    def parse_xiaohexia(self, response):
        # print(response.body.decode(response.encoding))
        # print(response.xpath('//table[2]/tbody/tr[contains(@class,"cells")]/td[2]/text()').extract_first())
        for proxy in json.loads(response.body.decode(response.encoding)):
            item = ProxyIpItem()
            item['proxy'] = proxy
            yield item

    def parse_nntime(self, response):
        # print(response.body.decode(response.encoding))
        # print(response.xpath('//table[2]/tbody/tr[contains(@class,"cells")]/td[2]/text()').extract_first())

        for tr in response.xpath('//*[@id="proxylist"]/tbody/tr'):
            item = ProxyIpItem()
            div = tr.xpath('./td[2]')
            script = div.xpath('./script/text()').extract_first() or ''
            temp = div.xpath('string(.)').extract()[0]
            ip_port = temp.replace(script, "")
            if ip_port:
                item['proxy'] = ip_port.strip()
                yield item

    def parse_cool_proxy(self, response):
        # print(response.body.decode(response.encoding))
        # print(response.xpath('//table[2]/tbody/tr[contains(@class,"cells")]/td[2]/text()').extract_first())

        for tr in response.xpath('//*[@id="main"]/table//tr'):
            item = ProxyIpItem()
            port = tr.xpath('./td[2]/text()').extract_first() or ''
            if port:
                ip = ''
                for span in tr.xpath('./td[1]/span/span[not(@style="display:none")]'):
                    num = span.xpath('./text()').extract_first() or ''
                    ip = "{}.{}".format(ip, num)
                item['proxy'] = "{}:{}".format(ip.strip('.'), port)
                yield item
