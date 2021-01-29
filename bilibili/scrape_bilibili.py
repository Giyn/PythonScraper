# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 21:31:50 2020

@author: Giyn
"""

import requests
from bs4 import BeautifulSoup
from selenium import webdriver # 引入浏览器驱动
from selenium.webdriver.common.by import By # 借助By模块进行操作
from selenium.webdriver.support.ui import WebDriverWait # 显式等待
from selenium.webdriver.support import expected_conditions as Ec # 显式等待的条件
import pandas as pd


browser = webdriver.Chrome() # 获取浏览器对象
WAIT = WebDriverWait(browser,10) # 指定最长等待时间

url = 'https://www.bilibili.com'
print('开始访问b站……')
browser.get(url)


def search(content):
    """
    
    在搜索框输入内容
    Parameters
    ----------
    content : string
        输入内容

    Returns
    -------
    None.

    """
    print('正在进行搜索……')
    # 用XPath选取节点
    input = WAIT.until(Ec.presence_of_element_located((By.XPATH,'//*[@id="nav_searchform"]/input')))
    submit = WAIT.until(Ec.element_to_be_clickable((By.XPATH,'//*[@id="nav_searchform"]/div/button')))

    # 从搜索框输入并点击搜索
    input.send_keys(content)
    submit.click()


def crawl():
    """
    
    爬取网页
    Raises
    ------
    Exception
        状态码非200

    Returns
    -------
    htmls : HTML
        返回的HTML

    """
    htmls = [] # 存放每个页面的HTML
    # 用for循环爬取每一个页面并获得其HTML
    for i in range(5):
        # 用f+字符串来表示每一个页面的网址
        url = f"https://search.bilibili.com/all?keyword=%E5%8D%8E%E6%99%A8%E5%AE%87&from_source=nav_search_new&page={str(int(i+1))}"
        r = requests.get(url) # 返回Response对象
        if r.status_code != 200: # 状态码检测
            raise Exception("error")
        htmls.append(r.text) # r.text是字符串类型

    return htmls


def parse(htmls):
    """
    
    解析网页
    Parameters
    ----------
    htmls : HTML
        爬取到的HTML网页

    Returns
    -------
    items : dict
        视频信息

    """
    videos = [] # 存放每个视频解析出来的HTML
    print('解析页面中……')
    for html in htmls:
        soup = BeautifulSoup(html, 'html.parser') # 解析每个页面
        # 获取每个视频的标签树
        video = soup.find(class_ = "video-list clearfix").find_all(class_="video-item matrix")
        videos.extend(video) # 列表存入列表，所以用extend()函数

    items = [] # 存放每个视频的各个项目
    print('正在爬取相关信息……')
    for video in videos:
        item = {} # 每个字典存放每个视频的相关信息
        item['视频标题'] = video.find('a')['title'] # 获取标签属性
        item['视频地址'] = video.find('a')['href']
        item['简介'] = video.find(class_ = 'des hide').string # 获取NavigableString
        item['观看次数'] = video.find(class_ = 'so-icon watch-num').get_text() # 获取目标路径下的子孙字符串
        item['发布时间'] = video.find(class_ = 'so-icon time').get_text()
        item['弹幕数量'] = video.find(class_ = 'so-icon hide').get_text()
        items.append(item) # 字典存入列表，所以用append()函数
        
    return items


def save_to_csv(items):
    """
    
    保存数据到csv
    Parameters
    ----------
    items : dict
        电影信息

    Returns
    -------
    None.

    """
    print('成功将数据写入文件！')
    # 将爬取的数据写入csv文件
    df = pd.DataFrame(items) # 用DataFrame构造数据框
    df.to_csv("华晨宇.csv")


def main():
    """
    
    主函数
    Returns
    -------
    None.

    """
    try:
        search('华晨宇')
        htmls = crawl()
        items = parse(htmls)
        save_to_csv(items)
    finally:
        print('爬取信息成功！')
        browser.close()


if __name__ == '__main__':
    main()