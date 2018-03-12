from client.core import Core
from client.core import TablesOP
from client.core import commandShowTables
from crypto_rsa.safeInput import safeInput

if __name__ == '__main__':
    account = input("输入帐号：")
    passwd = safeInput().getpass("请输入密码：")
    client = Core(account, passwd)
    client.login()
    originalTablesDict = client.getOriginalTablesDict("2017", "2")
    formatDict = TablesOP().setFormatDict(originalTablesDict)

    cmd = commandShowTables(formatDict)
    while 1:
        cmd.showTables()
        print("p:上一周,n:下一周")
        ws = input("输入第  周,继续查看\n> ")
        if ws == "p":
            ws = cmd.Ws
            ws -= 1
            if ws <= 0:
                ws = 1
        elif ws == "n":
            ws = cmd.Ws
            ws += 1
        cmd.setWs(ws)

