# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

# 书籍项目
class BooksItem(scrapy.Item):
    name = scrapy.Field()  # 书名
    price = scrapy.Field()  # 价格
    review_rating = scrapy.Field()  # 评价等级
    review_num = scrapy.Field()  # 评价数量
    upc = scrapy.Field()  # 产品编码
    stock = scrapy.Field()  # 库存量
