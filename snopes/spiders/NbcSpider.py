import json
import requests
import scrapy
import bs4
import re
from snopes.items import SnopesItem
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from scrapy.http import HtmlResponse
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

class NYTimes(scrapy.Spider):
    name = "NYTimes"
    allowed_domains = ["www.nytimes.com"]
    start_urls = ["https://www.nytimes.com/section/politics"]
    ua = UserAgent(browsers=["chrome"])

    def __init__(self, *args, **kwargs):
        super(NYTimes, self).__init__(*args, **kwargs)
        chrome_driver_path = "C:/Users/lenovo/AppData/Local/Google/Chrome/Application/chromedriver.exe"
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")
        self.service = Service(chrome_driver_path)
        self.driver = webdriver.Chrome(service=self.service, options=chrome_options)
        self.count = 0

    def parse(self, response):
        self.driver.get(response.url)
        time.sleep(10)  # 等待页面加载
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.count = self.count + 1
            # 获取当前页面的HTML内容并传递给Scrapy
            page_source = self.driver.page_source
            fake_response = HtmlResponse(url=self.driver.current_url, body=page_source, encoding='utf-8')
            yield from self.parse_articles(fake_response)
            # yield response.follow(self.driver.current_url, self.parse_article, headers={"User-Agent": self.ua.random})
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)  # 等待新内容加载
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if self.count > 200:
                break
            if new_height == last_height:
                break
            last_height = new_height
        
    def parse_articles(self, response): #  processing responses and extracting data
        
        for article in response.css('.css-18yolpw'):
            item = SnopesItem()
            item["title"] = article.css('div:nth-child(1) > article:nth-child(1) > a:nth-child(2) > h3:nth-child(1)::text').get()
            item["date"] = article.css('div:nth-child(1) > div:nth-child(2) > span:nth-child(1)::text').get()
            item["url"] = response.urljoin(article.css('div:nth-child(1) > article:nth-child(1) > a:nth-child(2)::attr(href)').get())
            item["claim"] = response.css('div:nth-child(1) > article:nth-child(1) > p:nth-child(3)::text').get()
            item["rating"] = "True"
            item["site"] = "NYTimes"
            item["tag"] = "NYTimes"
            yield item
        