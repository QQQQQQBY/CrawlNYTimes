import json

import scrapy
import fake_useragent

from snopes.items import SnopesItem


class LeadstoriesionSpider(scrapy.Spider):
    name = "leadstories"
    allowed_domains = ["leadstories.com"]
    start_urls = ["https://leadstories.com/cgi-bin/mt/mt-search.fcgi?search=&IncludeBlogs=1&blog_id=1&archive_type=Index&limit=10&page=1"]
    ua = fake_useragent.UserAgent(browsers=["chrome"])

    def parse(self, response):
        # follow links to article pages
        for article in response.css(".striped-list > li"):
            href = article.css(".mod-default-article > a::attr(href)").extract_first()
            # head_image_url = article.css("img::attr(data-ezsrcset)").extract_first().split(",")[0].split(" ")[0].strip()
            yield response.follow(href, self.parse_article, headers={"User-Agent": self.ua.chrome})

        # follow pagination links
        for href in response.css(".pagination > a[aria-label='Navigate to last page']::attr(href)"):
            yield response.follow(href, self.parse, headers={"User-Agent": self.ua.random})

    def parse_article(self, response):
        item = SnopesItem()
        selector = scrapy.Selector(text=response.text)
        item["url"] = response.url
        item["title"] = selector.css("hgroup > h1::text").extract_first("")
        for x in selector.css("script[type='application/ld+json']::text").extract():
            y = json.loads(x)
            if y.get("@type", "") and y["@type"].strip() == "NewsArticle":
                item["date"] = y.get("datePublished", "")
                break
        else:
            item["date"] = ""
        item["claim"] = selector.css(".mod-full-article-content > blockquote").extract_first("")
        item["rating"] = selector.css(".caption-overlay::text").extract_first("")
        item["head_image_url"] = selector.css(".fixed-media > picture > img::attr(src)").extract_first("")
        item["body"] = selector.css(".mod-full-article-content > blockquote ~ *").extract()
        item["sources"] = selector.css(".is-ellipsis::text").extract()
        item["site"] = "leadstories"
        yield item
