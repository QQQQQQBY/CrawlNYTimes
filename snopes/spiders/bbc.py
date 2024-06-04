import json

import scrapy
import fake_useragent

from snopes.items import SnopesItem


class BbcSpider(scrapy.Spider):
    name = "bbc"
    allowed_domains = ["dracos.co.uk", "bbc.com", "bbc.co.uk"]
    start_urls = ["http://dracos.co.uk/"]
    ua = fake_useragent.UserAgent(browsers=["chrome"])

    def start_requests(self):
        base_url = "https://dracos.co.uk/made/bbc-news-archive/"
        years = range(2024, 2025)
        for y in years:
            url = base_url + str(y)
            # headers={"User-Agent": self.ua.random} 有一个特定的目的：它为 Scrapy 蜘蛛发出的每个 HTTP 请求设置 User-Agent 标头。
            # User-Agent 标头是 HTTP 请求标头的一部分。它包含有关发出请求的客户端（例如 Web 浏览器或机器人）的信息。此信息通常包括客户端软件的名称和版本、操作系统以及其他相关详细信息
            # 避免阻止：许多网站实施措施来阻止或限制来自网络爬虫或机器人的请求，以防止服务器过载或抓取其内容。通过随机化用户代理，请求似乎来自不同的浏览器或设备，从而使网站更难以仅根据用户代理字符串来检测和阻止蜘蛛
            # 当 Scrapy 向 URL 发送请求时，它需要知道如何处理收到的响应。回调参数告诉Scrapy调用哪个方法来处理响应。在这种情况下，callback=self.parse_year意味着蜘蛛的parse_year方法将通过响应对象被调用。
            yield scrapy.Request(url=url, callback=self.parse_year, headers={"User-Agent": self.ua.random})

    def parse_year(self, response):
        for calender in response.css(".calendar"):
            for url in calender.css("td > a::attr(href)").extract():
                yield response.follow(url, callback=self.parse_day, headers={"User-Agent": self.ua.random})

    def parse_day(self, response):
        # 使用 CSS 选择器从响应的 HTML 中选择元素。响应对象包含所请求网页的 HTML 内容
        # td：选择 HTML 中的所有 <td> 元素（表格单元格）。
        # >：子组合器。它指定下一个元素必须是前一个元素的直接子元素。
        # a：选择作为 <td> 元素直接子代的所有 <a> 元素（锚链接）。
        # ::attr(href)：该伪类从选定的 <a> 元素中提取 href 属性的值。
        for url in response.css("td > a::attr(href)").extract():
            domains = url.split("/")
            if len(domains) > 2 and url.split("/")[-2].strip() == "news":
                yield response.follow(url, callback=self.parse_article, headers={"User-Agent": self.ua.random})

    def parse_article(self, response):
        if response.url.split("/")[-2].strip() != "news":
            return
        item = SnopesItem()
        selector = scrapy.Selector(text=response.text)
        item["url"] = response.url
        item["title"] = selector.css("#main-heading::text").extract_first("")
        for x in selector.css("script[type='application/ld+json']::text").extract():
            y = json.loads(x)
            if y.get("@type", "") and y["@type"].strip() == "ReportageNewsArticle":
                item["date"] = y.get("datePublished", "")
                break
        else:
            item["date"] = ""
        item["claim"] = selector.css("article header ~ div b::text").extract_first("")
        item["rating"] = "True"
        # item["head_image_url"] = selector.css("header ~ div[data-component='image-block'] img::attr(href)").extract_first("")
        # item["body"] = selector.css("article header ~ div").extract()
        # item["sources"] = ""
        item["site"] = "bbc"
        item["tag"] = "bbc"
        yield item
