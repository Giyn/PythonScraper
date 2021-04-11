# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 22:22:13 2020

Author: Giyn
GitHub: https://github.com/Giyn
Email : giyn.jy@gmail.com

"""

import logging
import re
import time

import pymongo
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
INDEX_URL = 'https://gz.meituan.com/meishi/b1184/pn{page}/'
TIME_OUT = 30
TOTAL_PAGE = 12
option = ChromeOptions()
option.add_argument("--disable-blink-features=AutomationControlled")
option.add_experimental_option('excludeSwitches', ['enable-automation'])
option.add_experimental_option('useAutomationExtension', False)
browser = webdriver.Chrome(options=option)
wait = WebDriverWait(browser, TIME_OUT)

MONGO_CONNECTION_STRING = 'mongodb://localhost:27017'  # MongoDB connection string
MONGO_DB_NAME = 'food'  # database name
MONGO_COLLECTION_NAME = 'meituan_college_town_food'  # collection name

client = pymongo.MongoClient(MONGO_CONNECTION_STRING)  # create MongoDB connection object
db = client['food']  # specify the database
collection = db['meituan_college_town_food']  # designated collection


def scrape_page(url, condition, locator):
    """
    Page scraping framework

    Args:
        url: pages to be scraped
        condition: judgement conditions for page loading
        locator: locator
    Returns:
        None
    """
    logging.info('scraping %s', url)
    try:
        browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument',
                                {'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'})
        time.sleep(1)
        browser.get(url)

        # scroll to the bottom
        browser.execute_script('window.scrollTo(0, document.body.scrollHeight)')

        try:
            # login
            if browser.title == '登录 | 美团网':
                browser.find_elements_by_xpath('//*[@id="login-email"]')[0].send_keys('phoneNumber')
                time.sleep(1)
                browser.find_elements_by_xpath('//*[@id="login-password"]')[0].send_keys('password')
                time.sleep(1)
                browser.find_element_by_xpath("//*[@id='J-normal-form']//input[@type='submit']").click()
                time.sleep(1)
        except IndexError:
            logging.info('logged')

        wait.until(condition(locator))
    except TimeoutException:
        logging.error('error occurred while scraping %s', url, exc_info=True)


def scrape_index(page):
    """
    Scrape every page

    Args:
        page:
    Returns:
        None
    """
    url = INDEX_URL.format(page=page)
    scrape_page(url, condition=EC.visibility_of_all_elements_located,
                locator=(By.XPATH, '//ul[@class="list-ul"]/li'))


def parse_index():
    """
    Get the url of each business

    Args:

    Returns:
        generator
    """
    elements = browser.find_elements_by_xpath('//*[@id="app"]//ul[@class="list-ul"]//a')
    for element in elements:
        url = element.get_attribute('href')
        yield url


def scrape_detail(url):
    """
    Scrape the page of each business

    Args:
        url
    Returns:
        None
    """
    scrape_page(url, condition=EC.visibility_of_element_located,
                locator=(By.XPATH, "//div[@class='d-left']/div[@class='name']"))


def parse_detail():
    """
    Parse the information of each business

    Args:
        None
    Returns:
        data
    """
    try:
        name = browser.find_element_by_xpath(
            "//div[@class='d-left']/div[@class='name']").text.strip('食品安全档案').strip()
    except:
        name = '无'
    try:
        star = browser.find_element_by_xpath("//div[@class='score clear']//p").text[0]
    except:
        star = '无'
    if star == '暂':
        star = '无'
    try:
        per_capita_consumption = browser.find_element_by_xpath(
            "//div[@class='score clear']//p/span").text.strip().strip('人均')
    except:
        per_capita_consumption = '无'
    try:
        address = browser.find_element_by_xpath("//div[@class='address']/p[1]").text.strip('地址：')
    except:
        address = '无'
    try:
        telephone = browser.find_element_by_xpath("//div[@class='address']/p[2]").text.strip('电话：')
    except:
        telephone = '无'
    try:
        business_hours = browser.find_element_by_xpath("//div[@class='address']/p[3]").text.strip(
            '营业时间：')
    except:
        business_hours = '无'
    try:
        raw_recommended_dishes = browser.find_element_by_xpath(
            "//div[@class='recommend']/div/ul").text
        recommended_dishes = ','.join(re.findall(u"[\u4e00-\u9fa5]+", raw_recommended_dishes))
    except:
        recommended_dishes = '无'
    try:
        review_people = browser.find_element_by_xpath(
            "//div[@class='comment']//div[@class='total']").text.strip('条网友点评').strip(
            '质量排序时间排序').strip()
    except:
        review_people = '无'
    url = browser.current_url
    try:
        cover = browser.find_element_by_xpath(
            "//div[@class='big']/div[@class='imgbox']/img").get_attribute('src')
    except:
        cover = '无'

    return {"NAME": name, "STAR": star, "PER_CAPITA_CONSUMPTION": per_capita_consumption,
            "ADDRESS": address,
            "TELEPHONE": telephone, "BUSINESS_HOURS": business_hours,
            "RECOMMENDED_DISHES": recommended_dishes,
            "REVIEW_PEOPLE": review_people, "URL": url, "COVER": cover}


def save_to_MongoDB(data):
    """
    Store data in MongoDB database

    Args:
        data
    Returns:
        None
    """
    collection.update_one({
        'NAME': data.get('NAME')
    }, {
        '$set': data
    }, upsert=True)


if __name__ == "__main__":
    for each_page in range(1, TOTAL_PAGE + 1):
        scrape_index(each_page)
        detail_urls = parse_index()
        for detail_url in list(detail_urls):
            scrape_detail(detail_url)
            detail_data = parse_detail()
            save_to_MongoDB(detail_data)
            logging.info('save data %s', detail_data)
