import json

import scrapy
import bs4
import re
from snopes.items import SnopesItem


class TruthorfictionSpider(scrapy.Spider):
    name = "truthorfiction"
    allowed_domains = ["www.truthorfiction.com"]
    start_urls = ["https://www.truthorfiction.com/category/fact-checks/politics/"]

    def parse(self, response):
        # follow links to article pages
        for article in response.css("article"):
            href = article.css("a::attr(href)").extract_first()
            yield response.follow(href, self.parse_article)

        # check if there is a next page
        next_page = response.css(".next::attr(href)").extract_first()
        if next_page:
            yield response.follow(next_page, self.parse, headers={"User-Agent": self.ua.random})
        # # follow links to article pages
        # for article in response.css("article"):
        #     href = article.css("a::attr(href)").extract_first()
        #     # head_image_url = article.css("img::attr(data-ezsrcset)").extract_first().split(",")[0].split(" ")[0].strip()
        #     yield response.follow(href, self.parse_article)

        # # follow pagination links
        # for href in response.css(".nav-previous > a::attr(href)"):
        #     yield response.follow(href, self.parse)

    def parse_article(self, response):
        item = SnopesItem()
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        selector = scrapy.Selector(text=soup.prettify())
        item["url"] = response.url
        item["title"] = selector.css("header > h1::text").extract_first("")
        yoast_schema_text = selector.css("#wpsso-schema-graph::text").extract_first()
        if yoast_schema_text:
            yoast_schema = json.loads(yoast_schema_text)
            for x in yoast_schema["@graph"]:
                if x["@type"] == "WebPage":
                    item["date"] = x.get("datePublished", "")
        else:
            item["date"] = ""
        # for x in json.loads(selector.css(".yoast-schema-graph::text").extract_first())["@graph"]:
        #     if x["@type"] == "WebPage":
        #         item["date"] = x.get("datePublished", "")
        item["claim"] = selector.css(".claim").extract_first("")
        match = re.search(r'<p class="claim">\s*<strong>\s*Claim:\s*<\/strong>\s*(.*?)\s*<\/p>', item["claim"])
        item["claim"] = match.group(1).strip()
        item["rating"] = selector.css(".rating > span::text").extract_first("")
        # item["head_image_url"] = ""
        # item["body"] = selector.css("#content .reporting-wrapper ~ *").extract()
        # item["sources"] = selector.css(".list-source-links > li").extract()
        item["site"] = "truthorfiction"
        item["tag"] = "politics"
        yield item
