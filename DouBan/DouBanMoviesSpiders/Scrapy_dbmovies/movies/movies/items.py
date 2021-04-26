# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MoviesItem(scrapy.Item):
    # define the fields for your item here like:

    ranking = scrapy.Field() # 排名
    name = scrapy.Field() # 电影名称
    director_actor = scrapy.Field() # 导演主演
    info = scrapy.Field() # 年份、国家、电影类型
    rating_score = scrapy.Field() # 评分
    rating_num = scrapy.Field() # 评论人数
    introduce = scrapy.Field() # 简介