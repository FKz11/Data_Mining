# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from .settings import BOT_NAME
from pymongo import MongoClient


class GbParsePipeline:
    def process_item(self, item, spider):
        return item


class GbMongoPipeline:
    def __init__(self):
        client = MongoClient()
        self.db = client[BOT_NAME]

    def process_item(self, item, spider):
        self.db[spider.name if isinstance(item, dict) else item.__class__.__name__].insert_one(item)
        return item


class GbImageDownloadPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item["data"].get("photo"):
            yield Request(item["data"]["photo"])

    def item_completed(self, results, item, info):
        if item["data"].get("photo"):
            item["data"]["photo"] = results[0][1]
        return item
