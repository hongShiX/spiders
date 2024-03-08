# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AcademicItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    unique_key = scrapy.Field()
    sourse_url = scrapy.Field()
    download_url = scrapy.Field()
    create_time = scrapy.Field()
    website_name = scrapy.Field()
    release_time = scrapy.Field()
    content = scrapy.Field()
    title = scrapy.Field()

