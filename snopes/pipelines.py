# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
import csv
from pathlib import Path
import re

from itemadapter import ItemAdapter
from w3lib import html
from scrapy.selector import Selector

from utils import uri_validator


class SnopesPipeline:
    def process_item(self, item, spider):
        item["url"] = item["url"].strip(" \n\t\r")
        item["title"] = item["title"].strip().replace("\n", " ").replace("\r", " ").replace("\t", " ").replace("  ", " ")
        item["date"] = item["date"].strip(" \n\t\r")
        item["claim"] = item["claim"].strip().replace("\n", " ").replace("\r", " ").replace("\t", " ").replace("  ", " ")
        # item["rating"] = item["rating"].strip(" \n\t\r")


        dir_path = Path("data")
        dir_path.mkdir(parents=True, exist_ok=True)
        file_path = dir_path / f"{spider.name}-{item['tag']}-{item['site']}.csv"

        if not os.path.isfile(file_path):
            is_first_write = 1
        else:
            is_first_write = 0
        # , 'head_image_url', 'body', 'sources'
        header = [
            'url', 'title', 'date', 'claim', 'rating', 'site'
        ]

        if item:
            with open(file_path, 'a', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                if is_first_write:
                    writer.writerow(header)
                writer.writerow(
                    [item[key] for key in header])
        return item
