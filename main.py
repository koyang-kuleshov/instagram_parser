from scrapy.crawler import CrawlerProcess
from scrapy.crawler import Settings

from insta_parse import settings
from insta_parse.spiders.config import login, passwd
from insta_parse.spiders.instagram import InstagramSpider

if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    crawler_proc = CrawlerProcess(settings=crawler_settings)

    # Заменить natgeo на нужный профиль
    crawler_proc.crawl(InstagramSpider, login, passwd, ['natgeo'])

    crawler_proc.start()
