# 69xinshu_spider

# 功能实现
+ 爬取69书吧排行榜的小说，并存入数据库，再用flask呈现再网页上

# 工具
+ python 3.10
+ flask web框架
+ mysql数据库

# 主要思路：
+ 通过spider.py将网站排行榜的小说的信息抓取至mysql数据库内，如小说正文，书名，作者名，简介
+ 通过app.py 使用flask web框架将数据库内数据渲染至网页端
+ 网页端功能实现
  + 收藏 ：/bookmark 对应数据库bookmark表
  + 历史阅读：/history 对应数据库history表
  + 小说阅读 /article表示小说页面，/article/id 表示章节页面 ，/article/id/chapter_number表示小说正文，对应小说正文表和书名表
  + 登录与注册：对应user表
+ login_required(f)定义装饰器用于限制只有用户登录后才能访问某些视图函数
+ @app.context_processor定义上下文处理器，可以向模板上下文注入额外的变量，在渲染模板时可以直接在模板中访问这些变量
    
