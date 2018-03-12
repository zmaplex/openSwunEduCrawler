# 西南民族大学 正方教务系统爬虫

这是一个业余作品，用 Python 获取教务系统的课程安排信息，并绘制显示课表。

## 核心登录

  client.core.py
  
  登录成功后，该类会返回一个 requests.session() 对象，
  可以使用这个对象对教务系统进行 POST 和 GET 请求。
  里面的代码仅供参考，各个学校教务系统细节可能存在差异。
  
  需要对 core.py 文件进行重写
  
  crypto_rsa 包下封装了 JS 加密方法，可以直接进行调用，返回结果与网页JS方法一致
  
  
##  演示

这是我的课表的演示

![demo](https://raw.githubusercontent.com/zyqf/openSwunEduCrawler/master/demo.gif)
