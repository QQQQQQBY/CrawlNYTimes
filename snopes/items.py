# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SnopesItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    date = scrapy.Field()
    claim = scrapy.Field()
    rating = scrapy.Field()
    # head_image_url = scrapy.Field()
    # body = scrapy.Field()
    # sources = scrapy.Field()
    site = scrapy.Field()
    tag = scrapy.Field()
    # image_urls = scrapy.Field()
