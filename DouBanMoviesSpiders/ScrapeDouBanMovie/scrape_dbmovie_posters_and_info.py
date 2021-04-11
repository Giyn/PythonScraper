# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 21:38:15 2020

@author: Giyn
"""

import os

import pandas as pd
import requests
from fake_useragent import UserAgent
from lxml import etree  # 解析HTML

ua = UserAgent()


def get_html(url):
    """

    获取HTML页面
    Parameters
    ----------
    url : string
        URL链接

    Returns
    -------
    HTML
        HTML页面

    """
    try:
        html = requests.get(url, headers={'User-Agent': ua.chrome})
        html.encoding = html.apparent_encoding
        if html.status_code == 200:
            print("获取HTML页面成功！")
    except Exception as e:
        print("获取HTML页面失败，原因是：%s" % e)

    return html.text


def parse_html(html):
    """

    解析HTML页面
    Parameters
    ----------
    html : HTML
        爬取的HTML页面

    Returns
    -------
    movies : list
        电影信息
    imgurls : list
        电影海报图片

    """
    movies = []  # 存储电影的相关信息
    imgurls = []  # 存储电影海报图片

    html = etree.HTML(html)
    lis = html.xpath("//ol[@class='grid_view']/li")  # XPath返回列表对象

    # 提取每一部电影的相关信息
    for li in lis:
        # 下面的XPath路径前面都要加上. 表示从li这个节点开始
        name = li.xpath(".//a/span[@class='title'][1]/text()")[0]  # 获取到的列表第0个元素才是电影名字
        director_actor = li.xpath(".//div[@class='bd']/p/text()[1]")[0].replace(' ', '').replace('\n', '').replace('/', '').replace('\xa0', '')  # 去除字符串中的多余字符
        info = li.xpath(".//div[@class='bd']/p/text()[2]")[0].replace(' ', '').replace('\n', '').replace('\xa0', '')  # 去除字符串中的多余字符
        rating_score = li.xpath(".//span[@class='rating_num']/text()")[0]
        rating_num = li.xpath(".//div[@class='star']/span[4]/text()")[0]
        introduce = li.xpath(".//p[@class='quote']/span/text()")

        # 把提取的相关信息存入movie字典，顺便处理Top 247那部电影没有introduce的情况
        if introduce:
            movie = {'name': name, 'director_actor': director_actor, 'info': info,
                     'rating_score': rating_score,
                     'rating_num': rating_num, 'introduce': introduce[0]}
        else:
            movie = {'name': name, 'director_actor': director_actor, 'info': info,
                     'rating_score': rating_score,
                     'rating_num': rating_num, 'introduce': None}

        movies.append(movie)

        imgurl = li.xpath(".//img/@src")[0]  # 提取图片URL
        imgurls.append(imgurl)

    return movies, imgurls


def download_img(url, movie):
    """

    保存海报图片
    Parameters
    ----------
    url : string
        图片文件链接
    movie : dict
        电影信息

    Returns
    -------
    None.

    """
    img = requests.get(url).content  # 返回的是bytes型也就是二进制的数据

    with open(movie['name'] + '.jpg', 'wb') as f:
        f.write(img)


if __name__ == '__main__':
    MOVIES = []
    IMGURLS = []

    for i in range(10):
        url = "https://movie.douban.com/top250?start=" + str(i * 25) + "&filter="
        html = get_html(url)
        movies = parse_html(html)[0]
        imgurls = parse_html(html)[1]

        MOVIES.extend(movies)
        IMGURLS.extend(imgurls)

    if 'movieposter' in os.listdir():
        pass
    else:
        os.mkdir('movieposter')

    os.chdir('movieposter')

    for i in range(250):
        download_img(IMGURLS[i], MOVIES[i])
        print("正在下载第" + str(i + 1) + "张图片……")

    os.chdir('../')  # 记得把路径换回来

    moviedata = pd.DataFrame(MOVIES)  # 把电影相关信息转换为DataFrame数据格式
    moviedata.to_csv('movie.csv')
    print("电影相关信息存储成功！")
