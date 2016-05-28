# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ProductItem(scrapy.Item):
    category = scrapy.Field()
    subcategory = scrapy.Field()
    product_name = scrapy.Field()
    price = scrapy.Field()
    description = scrapy.Field()
    image_link = scrapy.Field()
    product_url = scrapy.Field()
    pass
