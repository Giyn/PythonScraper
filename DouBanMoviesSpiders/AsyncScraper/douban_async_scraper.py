"""
-------------------------------------
# -*- coding: utf-8 -*-
# @Time    : 2021/1/18 10:12:44
# @Author  : Giyn
# @Email   : giyn.jy@gmail.com
# @File    : douban_async_scraper.py
# @Software: PyCharm
-------------------------------------
"""

import asyncio
import json
import logging
import re

import aiohttp
from faker import Faker
from lxml import etree
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB 相关配置参数
MONGO_CONNECTION_STRING = 'mongodb://localhost:27017'
MONGO_DB_NAME = 'movies'
MONGO_COLLECTION_NAME = 'AsyncScraper'
client = AsyncIOMotorClient(MONGO_CONNECTION_STRING)
db = client[MONGO_DB_NAME]
collection = db[MONGO_COLLECTION_NAME]

# 日志参数配置
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')

INDEX_URL = 'https://movie.douban.com/j/new_search_subjects?sort=U&range=0,10&tags=&start={index}'
DETAIL_URL = 'https://movie.douban.com/subject/{id}/'
PAGE_SIZE = 10  # 页数
CONCURRENCY = 5  # 并发量
semaphore = asyncio.Semaphore(CONCURRENCY)
session = None
fake = Faker()


async def scrape_api(url):
    """

    scrape api

    Args:
        url: url

    Returns:
        html

    """
    async with semaphore:
        try:
            logging.info('Scraping %s', url)
            async with session.get(url, headers={'User-Agent': fake.user_agent()}) as response:
                return await response.text()
        except aiohttp.ClientError:
            logging.error('ERROR')


async def scrape_index(page):
    """

    scrape by index

    Args:
        page: page

    Returns:
        the result of scrape api

    """
    url = INDEX_URL.format(index=20 * page)
    return await scrape_api(url)


async def save_data(data):
    """

    save data

    Args:
        data: movies data

    Returns:
        collection saving

    """
    logging.info('Saving Data %s', data)
    if data:
        return await collection.update_one({'id': data['id']}, {'$set': data}, upsert=True)


def parse_movie(html, id):
    """

    parse movie information

    Args:
        html: html

    Returns:
        movie dict

    """
    doc = etree.HTML(html)
    movie_info_xpath = "/html/body//div[@id='info']"

    try:
        movie_title = doc.xpath("/html/body//span[@property='v:itemreviewed']/text()")[0]
    except:
        movie_title = ''
    try:
        movie_year = re.findall(r'\d+', doc.xpath("/html/body//span[@class='year']/text()")[0])[0]
    except:
        movie_year = ''
    try:
        movie_director = doc.xpath("/html/body//div[@id='info']//a[@rel='v:directedBy']/text()")[0]
    except:
        movie_director = ''
    try:
        movie_writer = ','.join(re.findall('编剧: .+', doc.xpath(movie_info_xpath)[0].xpath('string(.)'))[0].split(": ")[1].split(' / '))
    except:
        movie_writer = ''
    try:
        movie_actor = ','.join(re.findall('主演: .+', doc.xpath(movie_info_xpath)[0].xpath('string(.)'))[0].split(": ")[1].split(' / '))
    except:
        movie_actor = ''
    try:
        movie_type = ','.join(doc.xpath("/html/body//div[@id='info']//span[@property='v:genre']/text()"))
    except:
        movie_type = ''
    try:
        movie_area = ','.join(re.findall('制片国家/地区: .+', doc.xpath(movie_info_xpath)[0].xpath('string(.)'))[0].split(": ")[1].split(' / '))
    except:
        movie_area = ''
    try:
        movie_language = re.findall('语言: [\u4e00-\u9fa5]+', doc.xpath(movie_info_xpath)[0].xpath('string(.)'))[0].split(": ")[1]
    except:
        movie_language = ''
    try:
        movie_date = re.findall('上映日期: .+', doc.xpath(movie_info_xpath)[0].xpath('string(.)'))[0].split(": ")[1].replace(' / ', ',')
    except:
        movie_date = ''
    try:
        movie_duration = re.findall(r'\d+分钟', doc.xpath(movie_info_xpath)[0].xpath('string(.)'))[0]
    except:
        movie_duration = ''
    try:
        movie_IMDb = re.findall('IMDb链接: .+', doc.xpath(movie_info_xpath)[0].xpath('string(.)'))[0].split(": ")[1]
    except:
        movie_IMDb = ''

    movie = {'title': movie_title, 'year': movie_year, 'director': movie_director,
             'writer': movie_writer, 'actor': movie_actor, 'type': movie_type, 'area': movie_area,
             'language': movie_language, 'date': movie_date, 'duration': movie_duration,
             'IMDb': movie_IMDb, 'id': id}

    return movie


async def scrape_detail(id):
    """

    scrape detailed movie

    Args:
        id: movie id

    """
    url = DETAIL_URL.format(id=id)
    html = await scrape_api(url)
    data = parse_movie(html, id)
    print(data)
    await save_data(data)


async def main():
    """

    main function

    """
    global session
    session = aiohttp.ClientSession()
    scrape_index_tasks = [asyncio.ensure_future(scrape_index(page)) for page in
                          range(0, PAGE_SIZE)]
    print(scrape_index_tasks)
    results = await asyncio.gather(*scrape_index_tasks)
    print(results)
    movies_dict = json.loads(results[0])
    try:
        movies_num = len(movies_dict['data'])
    except KeyError:
        logging.error('IP is banned!')
    movies_id = []
    for i in range(movies_num):
        movies_id.append(re.findall(r'\d+', movies_dict['data'][i]['url'])[0])

    scrape_detail_tasks = [asyncio.ensure_future(scrape_detail(id)) for id in movies_id]
    await asyncio.wait(scrape_detail_tasks)
    await session.close()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
