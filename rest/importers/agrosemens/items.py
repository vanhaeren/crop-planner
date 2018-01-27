# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AgrosemensItem(scrapy.Item):
    # define the fields for your item here like:
    variety = scrapy.Field()
    category = scrapy.Field()
    href = scrapy.Field()
    taxon = scrapy.Field()
    description = scrapy.Field()



