import json

import scrapy
from fake_useragent import UserAgent

from snopes.items import SnopesItem


class SnopesFactSpider(scrapy.Spider):
    name = "snopes_fact" # specifies the name of the spider
    allowed_domains = ["www.snopes.com"] #  domain names that the spider is allowed to crawl
    # base_url = 'https://www.snopes.com/tag/joe-biden/?pagenum={}'
    base_url = 'https://www.snopes.com/'
    start_urls = ["https://www.snopes.com/tag/joe-biden/"] # URLs that the spider will start crawling from
    ua = UserAgent()

    # def start_requests(self):
    #     for page in range(2,7):
    #         url = self.base_url.format(page)
    #         yield scrapy.Request(url,callback=self.parse)


    def parse(self, response): #  processing responses and extracting data
        # follow links to article pages
        for href in response.css(".outer_article_link_wrapper::attr(href)"):
            yield response.follow(href, self.parse_article,
                                  headers={"User-Agent": self.ua.random},)
        # receives a Response object and should return either Item objects, Request objects, or an iterable of either
        # follow pagination links
        for href in response.css(".next-button::attr(href)"):
            yield response.follow(href, self.parse,
                                  headers={"User-Agent": self.ua.random},)

    def parse_article(self, response):
        item = SnopesItem()
        item["url"] = response.url
        item["title"] = response.css(".title-container > h1::text").extract_first("")
        try:
            item["date"] = json.loads(response.css("script[type='application/ld+json']::text").extract_first())[
                "datePublished"]
        except:
            item["date"] = ""
        item["claim"] = response.css(".claim_cont::text").extract_first("")
        item["rating"] = response.css(".rating_title_wrap::text").extract_first("")
        # item["head_image_url"] = response.css("#cover-main::attr(src)").extract_first("")
        # item["body"] = response.css("#fact_check_rating_container ~ *").extract()
        # item["sources"] = response.css("#sources_rows > p").extract()
        item["site"] = "snopes"
        item["tag"] = "joe-biden"
        yield item
        # pass
