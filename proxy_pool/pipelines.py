# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from .validator import Validator


class ProxyPollPipeline(object):
    def __init__(self):
        self.proxies = []

    def process_item(self, item, spider):
        self.proxies.append("http://{}".format(item['proxy']))
        return item

    def close_spider(self, spider):
        validator = Validator()
        validator.main(self.proxies)
