import sys
import termios
import tty

"""
此脚本来自网络，具体出处找不到了
若侵犯您的权利，请联系QQ767026763@Gmail.com
"""
class safeInput(object):
    def __getch(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def getpass(self, tip, maskchar="*"):
        if tip:
            print(tip)
        password = ""
        while True:
            ch = self.__getch()
            if ch == "\r" or ch == "\n":
                print()
                return password
            elif ch == "\b" or ord(ch) == 127:
                if len(password) > 0:
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
                    password = password[:-1]
            else:
                if maskchar:
                    sys.stdout.write(maskchar)
                    sys.stdout.flush()
                password += ch


if __name__ == '__main__':
    x = input("please input your gitlab username:\n")
    print('please input your password:')
    y = safeInput().getpass()
    print('\nYour username is:' + x + ' and password is:' + y)
