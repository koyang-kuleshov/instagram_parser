# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import TakeFirst


class InstaParseItem(scrapy.Item):
    _id = scrapy.Field()
    user_name = scrapy.Field(output_processor=TakeFirst())
    user_id = scrapy.Field(output_processor=TakeFirst())
    post_photos = scrapy.Field()
    post_pub_date = scrapy.Field(output_processor=TakeFirst())
    like_count = scrapy.Field(output_processor=TakeFirst())
