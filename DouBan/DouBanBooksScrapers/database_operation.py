"""
-------------------------------------
# -*- coding: utf-8 -*-
# @Time    : 2021/4/27 1:57:56
# @Author  : Giyn
# @Email   : giyn.jy@gmail.com
# @File    : database_operation.py
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

# 建书籍表
create_books_table_sql = """
    CREATE TABLE `douban_book` (
    `book_name` VARCHAR(20) NOT NULL UNIQUE,
    `author` VARCHAR(20) NOT NULL,
    `press` VARCHAR(20),
    `publishing_year` VARCHAR(10),
    `score` FLOAT,
    `rating_num` INTEGER,
    `page_num` INTEGER,
    `price` VARCHAR(10),
    `ISBN` VARCHAR(30),
    `content_introduction` VARCHAR(2000),
    `cover_url` VARCHAR(100),
    `readers` VARCHAR(1000)
    )
"""

# 建用户表
create_users_table_sql = """
    CREATE TABLE `douban_book_users` (
    `id` VARCHAR(40) NOT NULL UNIQUE,
    `nickname` VARCHAR(40),
    `read_num` INTEGER,
    `read_book_and_score` TEXT
    )
"""


def main(sql: str):
    """

    主函数

    Args:

    Returns:

    """
    try:
        cursor.execute(sql)
    except Exception as e:
        logging.error(e)
        conn.rollback()


if __name__ == '__main__':
    main(create_users_table_sql)
