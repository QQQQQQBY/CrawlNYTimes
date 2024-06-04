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

class climatecentralSpider(scrapy.Spider):
    name = "climatecentral"
    allowed_domains = ["climatecentral.org"]
    start_urls = ["https://www.climatecentral.org/resources?page=2&tab=content&from=2023-05-01&to=2024-03-31"]
    ua = UserAgent()

    def __init__(self, *args, **kwargs):
        super(climatecentralSpider, self).__init__(*args, **kwargs)
        chrome_driver_path = "C:/Users/lenovo/AppData/Local/Google/Chrome/Application/chromedriver.exe"
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")  # 设置窗口大小
        self.service = Service(chrome_driver_path)
        self.driver = webdriver.Chrome(service=self.service, options=chrome_options)

    def parse(self, response):
        self.driver.get(response.url)
        time.sleep(10)  # 等待页面加载
        
        while True:
            page_source = self.driver.page_source
            response = HtmlResponse(url=self.driver.current_url, body=page_source, encoding='utf-8')
            
            # follow links to article pages
            for article in response.css("#panel-content > ul > li"):
                count = len(response.css("#panel-content > ul > li"))
                href = article.css("a::attr(href)").extract_first()
                yield response.follow(href, self.parse_article, headers={"User-Agent": self.ua.random})
            
            try:
                # 查找并点击下一页按钮
                next_button = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'li.next> a> button'))
                )
                if count < 12:
                    break
                # next_button.click()
                self.driver.execute_script("arguments[0].click();", next_button)

                time.sleep(5)  # 等待新内容加载

            except Exception as e:
                self.logger.info(f"No more pages to load: {e}")
                break


    def closed(self, reason):
        self.driver.quit()

    def parse_article(self, response):
        item = SnopesItem()
        # import os
        # os.environ["http_proxy"] = "http://localhost:10809"
        # os.environ["https_proxy"] = "http://localhost:10809"
        # responses = requests.get(response.url)
        # html_content = responses.content
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        # 使用BeautifulSoup解析HTML
        # soup = BeautifulSoup(html_content, "html.parser")
        article_body = soup.find("section", class_="styles_container__qtWEX styles_size-sm__I8r1t styles_richText__XJezY posts")
        item["url"] = response.url
        title_element = soup.find("h1")
        item["title"] = title_element.text.strip()
        if article_body:
            paragraphs = article_body.find_all("p")
            item["claim"] = "\n".join(paragraph.get_text(strip=True) for paragraph in paragraphs)
        else:
            print("无法找到正文内容")
        try:
            
            date_element = soup.select_one('.styles_label__2SmWY.styles_label__D4Igk')
            # 提取日期文本
            if date_element:
                date_text = date_element.get_text(strip=True)
                # print(date_text)
                match = re.search(r'•([A-Za-z]+\s+\d{1,2},\s+\d{4})', date_text)
                date = match.group(1)
                item["date"] = date
            else:
                print("Date element not found.")
        except:
            item["date"] = ""
        item["rating"] = True
        item["site"] = "climatecentral"
        item["tag"] = "climatecentral"
        yield item
