"""
-------------------------------------
# -*- coding: utf-8 -*-
# @Time    : 2021/4/29 12:33:26
# @Author  : Giyn
# @Email   : giyn.jy@gmail.com
# @File    : get_users.py
# @Software: PyCharm
-------------------------------------
"""

import logging

import pymysql

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')

conn = pymysql.connect(
    host="localhost",
    user="root",
    password="******",
    database="book",
    charset="utf8"
)

cursor = conn.cursor()  # 得到一个可以执行SQL语句的光标对象


if __name__ == '__main__':
    select_sql = 'SELECT readers FROM douban_book'

    num = cursor.execute(select_sql)
    users_url_tuple = cursor.fetchall()
    with open('user_urls.txt', mode='a+', encoding='utf-8') as file:
        for i in range(num):
            for url in users_url_tuple[i][0].replace('[', '').replace(']', '').replace('\'', '').split(','):
                file.write(url.strip() + '\n')
