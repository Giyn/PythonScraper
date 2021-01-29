# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from ..items import BooksItem # ..表示上级目录

class BooksSpider(scrapy.Spider):
    name = 'books_spider' # 爬虫名字
    allowed_domains = ['books.toscrape.com']
    start_urls = ['http://books.toscrape.com/']

    # 每一页的页面解析函数
    def parse(self, response):
        # 提取当前页面所有书的url
        le = LinkExtractor(restrict_xpaths='//article[@class="product_pod"]')
        for link in le.extract_links(response):
            yield scrapy.Request(url=link.url, callback=self.parse_book)

        # 提取下一页的url
        le = LinkExtractor(restrict_xpaths='//ul[@class="pager"]/li[@class="next"]/a')
        links = le.extract_links(response)
        if links:
            next_url = links[0].url
            yield scrapy.Request(url=next_url, callback=self.parse)

    # 每一本书的页面解析函数
    def parse_book(self, response):
        book = BooksItem() # 将信息存入BooksItem对象
        book['name'] = response.xpath('//div[@class="col-sm-6 product_main"]/h1/text()').extract_first()
        book['price'] = response.xpath('//p[@class="price_color"]/text()').extract_first()
        book['review_rating'] = response.xpath('//div[@class="col-sm-6 product_main"]/p[3]/@class') \
            .re_first('star-rating ([A-Za-z]+)') # \是续行符
        book['stock'] = response.xpath('//table[@class="table table-striped"]//tr[6]/td/text()').re_first('\((\d+) available\)')
        book['upc'] = response.xpath('//table[@class="table table-striped"]//tr[1]/td/text()').extract_first()
        book['review_num'] = response.xpath('//table[@class="table table-striped"]//tr[7]/td/text()').extract_first()

        yield book