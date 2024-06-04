# main.py
import sys
import os
# os.environ["http_proxy"] = "http://localhost:10809"
# os.environ["https_proxy"] = "http://localhost:10809"
from scrapy.cmdline import execute


def start_scrapy():
    # sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    # sys.path.append("C:/Users/lenovo/Desktop/reddit_new/AgentReddit/snopes/")
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # 运行单个爬虫
    execute(["scrapy", "crawl", "NYTimes"])


if __name__ == '__main__':
    start_scrapy()
