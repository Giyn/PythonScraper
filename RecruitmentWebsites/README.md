# Recruitment Websites
:paperclips: 爬取各大招聘网站：前程无忧、BOSS 直聘、智联招聘、猎聘网、拉勾网。

#### 环境的配置

编程语言：Python 3.7.7

使用的爬虫库：requests、pyppeteer

第三方库：参考 `requirements.txt` 文件

#### 浏览器调试模式

如图，爬虫程序使用的是浏览器自动化爬取。

<img src="https://i.loli.net/2021/04/01/9JXPW5RwLmTnjo1.png" alt="971d1a087f9ca46bdc50c0be2e88540.png" style="zoom:67%;" />

若用户需要查看所爬取页面，可将 `headless` 参数调为 False。

#### **如何模拟登录？**

1. 运行 `login.py` 文件；
2. 用户自行选择需要模拟登录的网站；
3. 用户手动登录网站；
4. 登录后即可关闭，程序自动生成 `userdata_{website}` 文件夹，相关信息即存储在里面，下次访问时可以保持登录状态。

#### 如何运行程序？

1. 直接运行 `job51.py`、`boss_zhipin.py`、`zhilian.py`、`liepin.py`、`lagou.py` 即可自动爬取数据，数据会统一存储到 `data.csv` 表格中；
2. 支持同时运行以上 5 个爬虫程序；
3. 爬取完毕后，运行 `data_clear.py` 文件，进行数据的清洗（例如去重、去除缺失值严重的数据）；

#### 所爬网站：

- [前程无忧](https://www.51job.com/)
  
  - 网站特点：
    - 数据由 JavaScript 动态加载，难以捕获到 Ajax 请求。
    - 不会封 IP，可以高并发爬取。
    
  - 爬取方法：
    
    - 无需模拟登录；
    
    - 使用 Pyppetter 框架，模拟浏览器行为，异步爬取。
- [BOSS 直聘](https://www.zhipin.com/)
  
  - 网站特点：
    - 数据由 JavaScript 动态加载，难以捕获到 Ajax 请求。
  - 爬取方法：
    - 需要模拟登录；
    - 使用 Pyppetter 框架，模拟浏览器行为，异步爬取。
  
- [智联招聘](https://www.zhaopin.com/)

  - 网站特点：
    - 数据由 JavaScript 动态加载，在 Chrome 浏览器的开发者工具中无法捕获到 Ajax 请求，因此无法构造对应的 URL。
    
  - 爬取方法：

    - 需要模拟登录；

    - 使用 Pyppetter 框架，模拟浏览器行为，异步动态爬取。

- [猎聘网](https://www.liepin.com/)
  
  - 网站特点：
    - 数据由 JavaScript 动态加载，难以捕获到 Ajax 请求。
  - 爬取方法：
  
    - 需要模拟登录；
  
    - 使用 Pyppetter 框架，模拟浏览器行为，异步动态爬取。
  
- [拉勾网](https://www.lagou.com/)
  
  - 网站特点：
    - 数据由 JavaScript 动态加载，难以捕获到 Ajax 请求。
    - 翻页功能完全由 JavaScript 实现，翻页后 URL 不变，故通过模拟点击来翻页。
    
  - 爬取方法：
    
    - 需要模拟登录；
    
    - 使用 Pyppetter 框架，模拟浏览器行为，异步动态爬取。

#### 给数据添加序号

运行 `add_number.py` 文件即可给表格的第一列添加序号。