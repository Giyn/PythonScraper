# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from ..items import MoviesItem

class MoviesSpiderSpider(scrapy.Spider):

    name = 'movies_spider'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36', }
    # allowed_domains = ['movie.douban.com/top250']
    # start_urls = ['http://movie.douban.com/top250/']


    def start_requests(self):
        url = 'https://movie.douban.com/top250'
        yield Request(url, headers=self.headers)


    def parse(self, response):
        item = MoviesItem()
        movies = response.xpath('//ol[@class="grid_view"]/li')

        for movie in movies:
            item['ranking'] = movie.xpath('.//div[@class="pic"]/em/text()').extract()[0]
            item['name'] = movie.xpath('.//div[@class="hd"]/a/span[1]/text()').extract()[0]
            item['director_actor'] = movie.xpath('.//div[@class="bd"]/p/text()[1]').extract()[0].replace('\n','  ').replace(' ','').replace('/','') # 去除字符串中的多余字符
            item['info'] = movie.xpath('.//div[@class="bd"]/p/text()[2]').extract()[0].replace(' ','').replace('\n','').replace('\xa0', '') # 去除字符串中的多余字符
            item['rating_score'] = movie.xpath('.//div[@class="star"]/span[@class="rating_num"]/text()').extract()[0]
            item['rating_num'] = movie.xpath('.//div[@class="star"]/span[4]/text()').extract()[0]

            # 有一些电影没有简介
            if movie.xpath('.//p[@class="quote"]/span/text()').extract_first():
                item['introduce'] = movie.xpath('.//p[@class="quote"]/span/text()').extract()[0]
            else:
                item['introduce'] = '无'
            yield item

        next_url = response.xpath('//span[@class="next"]/a/@href').extract()
        if next_url:
            next_url = 'https://movie.douban.com/top250' + next_url[0]
            yield Request(next_url, headers=self.headers)
