# -*- coding:utf-8 -*-
import time
import requests

from lxml import html
from crypto_rsa.RSAJS import RSAKey
from crypto_rsa.base64 import Base64 as pB64


class Core(object):
    def __init__(self, account="", passwd=""):
        self.account = account
        self.password = passwd
        self.loginStatus = False
        self.client = requests.session()

    def setLoginInfo(self, account, passwd):
        self.account = account
        self.password = passwd

    def __getEnPassword(self, string, exponent, modulus):
        b64 = pB64()
        exponent = b64.b64_to_hex(exponent)
        modulus = b64.b64_to_hex(modulus)

        rsa = RSAKey()
        rsa.setPublic(modulus, exponent)
        crypto_t = rsa.encrypt(string)
        return b64.hex_to_b64(crypto_t)

    def getStudentInfo(self):
        # 获取学生的名字与专业
        params = (
            ('xt', 'jw'),
            ('localeKey', 'zh_CN'),
            ('_', self.account),
            ('gnmkdm', 'index'),
            ('su', self.account),
        )
        response = self.client.get('http://211.83.241.81/jwglxt/xtgl/index_cxYhxxIndex.html',
                                   params=params
                                   )
        tree = html.fromstring(response.text)

        self.stuName = tree.xpath('/html/body/div/div/h4/text()')[0]
        self.stuMajor = tree.xpath('/html/body/div/div/p/text()')[0]

    def login(self):
        if self.account is "" or self.password is "":
            raise NameError("Account or passwd is empty")
        ntime = int(time.time())
        indexUrl = "http://211.83.241.81/jwglxt/xtgl/login_slogin.html?language=zh_CN&_t={}".format(ntime)
        publicKeyUrl = "http://211.83.241.81/jwglxt/xtgl/login_getPublicKey.html?time={}&_={}".format(ntime, ntime - 10)
        bodyByGet = self.client.get(indexUrl)
        modExp = self.client.get(publicKeyUrl).json()
        tree = html.fromstring(bodyByGet.text)
        csrftoken = tree.xpath('//*[@id="csrftoken"]/@value')

        data = [
            ('csrftoken', csrftoken),
            ('yhm', self.account),
            ('mm', self.__getEnPassword(self.password, modExp["exponent"], modExp["modulus"])),
            ('mm', self.__getEnPassword(self.password, modExp["exponent"], modExp["modulus"]))
        ]
        headers = {
            'Origin': 'http://211.83.241.81',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Cache-Control': 'max-age=0',
            'Referer': indexUrl,
            'Connection': 'keep-alive',
            'DNT': '1',
        }

        response = self.client.post("http://211.83.241.81/jwglxt/xtgl/login_slogin.html",
                                    headers=headers,
                                    data=data)

        if "用户名或密码不正确，请重新输入" in response.text:
            print("登录状态:登录失败")
            raise NameError("Login failed")

        else:
            self.loginStatus = True
            self.getStudentInfo()
            print("登录状态:登录成功")
            print("欢迎您：{} 同学".format(self.stuName))
            print("专业:{}".format(self.stuMajor))
            return self.client

    def getOriginalTablesDict(self, year, semester):
        # xnm 所选学年  2017 就是 2017-2018, 2016 就是2016-2017
        # xqm 所需学期  3 是第一学期，12 是第二学期
        if self.loginStatus is not True:
            raise NameError("This is not logged in !")

        dic = {"1": "3", "2": "12"}
        classTableUrl = "http://211.83.241.81/jwglxt/kbcx/xskbcx_cxXsKb.html?gnmkdm=N253508"
        semester = dic[semester]
        data = [
            ("xnm", year),
            ("xqm", semester)
        ]
        response = self.client.post(classTableUrl,
                                    data=data
                                    )
        return response.json()


class Nestingdict(dict):

    def __missing__(self, key):
        value = self[key] = type(self)()
        return value


class TablesOP(object):
    def __init__(self):
        self.tables_dict = Nestingdict()

    def __format_time(self, String):
        String = String[:-1]
        result = []
        min, max = String.split("-")
        min = int(min)
        max = int(max)
        last_number = min + 1
        if max - min > 1:
            while 1:
                if last_number + 1 > max + 1:
                    break
                result.append("{}-{}".format(min, last_number))
                min = last_number + 1
                last_number = min + 1
            return result
        else:
            result.append(String)
            return result

    def __addTablesJson(self, item, keyword):
        class_time = self.__format_time(item["jc"])
        for c_item in class_time:
            c_detail = self.tables_dict[keyword][item["xqjmc"]][c_item]
            c_detail["room"] = item["cdmc"]  # 教学教室
            c_detail["school"] = item["xqmc"]  # 学区
            c_detail["teacher"] = item["xm"]  # 老师
            c_detail["period"] = item["zcd"]  # 教学时间
            c_detail["className"] = item["kcmc"]  # 教学时间

    def setFormatDict(self, dic):

        for item in dic["kbList"]:
            if "(单)" in item["zcd"]:
                self.__addTablesJson(item, "single")
            elif "(双)" in item["zcd"]:
                self.__addTablesJson(item, "double")
            else:
                self.__addTablesJson(item, "all")

        return self.tables_dict


class commandShowTables(object):

    def __init__(self, formatDict=None, startWeeks="2018-2-26"):
        import datetime

        date = tuple(map(int, startWeeks.split("-")))
        self.tablesDict = formatDict
        # startWeeks 开学日期的第几周
        self.startWeek = datetime.date(date[0], date[1], date[2]).isocalendar()[1]
        # natureWeek 今天日期的第几周
        self.natureWeek = datetime.datetime.now().isocalendar()[1]
        # Ws  现在已开学的第几周
        self.Ws = self.natureWeek - self.startWeek + 1
        print("\n现在是第{}周\n".format(self.Ws))

    def setWs(self, Ws):
        print("当前周由 第{}周 改为 第{}周".format(self.Ws, Ws))
        self.Ws = int(Ws)

    def setDict(self, formatDict):
        self.tablesDict = formatDict

    def getDetail(self, week, ctime):
        pass

    def showTables(self):
        # 格式化输出课表，每个人得到的JSON的字段可能不一样，可能需要完全重写
        from texttable import Texttable
        dataDict = self.tablesDict
        # 列字段
        cTimeList = ("1-2", "3-4", "5-6", "7-8", "9-10", "11-12")
        # 行字段
        navList = [" 课时|星期 ", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        # 选择单双周
        select = ["double", "single"][self.Ws % 2]

        # 初始化 Texttable
        tablesInfo = Texttable(max_width=160)
        tablesInfo.set_cols_align(["l", "c", "c", "c", "c", "c", "c", "c"])
        tablesInfo.add_row(navList)
        # ctime 课时，全天一共6节
        # 添加列
        for ctime in range(6):
            line = []
            # 添加为行
            for day in range(8):
                nowday = navList[day]
                nowcTime = cTimeList[ctime]
                if day == 0:
                    line.append(nowcTime)
                    continue
                if dataDict["all"][nowday][nowcTime]:
                    detail = dataDict["all"][nowday][nowcTime]
                    # 2-16周(双) => tuple (2,16)
                    period = list(map(int, detail["period"].split("周")[0].split("-")))
                    if self.Ws < period[0] or self.Ws > period[1]:
                        line.append("                ")
                        continue
                    str = " {:^10}\n\n{:^10}\n{:^10}\n{:^10} ".format(detail["className"], detail["room"],
                                                                      detail["teacher"],
                                                                      detail["period"], chr(12288))
                    line.append(str)

                elif dataDict[select][nowday][nowcTime]:
                    detail = dataDict[select][nowday][nowcTime]
                    # String "2-16周(双)" => tuple (2,16)
                    period = list(map(int, detail["period"].split("周")[0].split("-")))
                    if self.Ws < period[0] or self.Ws > period[1]:
                        line.append("                ")
                        continue
                    str = " {:^10}\n\n{:^10}\n{:^10}\n{:^10} ".format(detail["className"], detail["room"],
                                                                      detail["teacher"],
                                                                      detail["period"], chr(12288))
                    line.append(str)
                else:
                    line.append("                ")
            tablesInfo.add_row(line)
        print(tablesInfo.draw())


if __name__ == '__main__':
    # 课程安排 POST 查询入口

    classTableUrl = "http://211.83.241.81/jwglxt/kbcx/xskbcx_cxXsKb.html?gnmkdm=N253508"
    # xnm 所选学年  2017 就是 2017-2018, 2016 就是2016-2017
    # xqm 所需学期  3 是第一学期，12 是第二学期
    data = [
        ("xnm", "2017"),
        ("xqm", "12")
    ]
    client = Core("username", "passwd").login()
    response = client.post(classTableUrl,
                           data=data
                           )
    dic = response.json()
    b = TablesOP().setFormatDict(dic)
    a = commandShowTables(b)
    a.showTables()
