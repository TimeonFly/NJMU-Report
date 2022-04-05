import re
import requests
import time
import smtplib
import yaml
from encrypt import AESEncrypt
from email.mime.text import MIMEText
from email.header import Header


class LoginError(Exception):
    pass


class SchoolLogin:
    def __init__(self):
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Origin': 'http://authserver.njmu.edu.cn',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.84'}
        self.session = requests.Session()

    def main_login(self):  # 网上办事大厅登录函数
        with open('ID.yaml', 'r', encoding='utf-8') as f:
            bs_id = yaml.load(f.read())['id']
        username = bs_id['username']
        password = bs_id['password']
        url1 = 'http://authserver.njmu.edu.cn/authserver/login?service=http%3A%2F%2Fehall.njmu.edu.cn%2Flogin%3Fservice%3Dhttp%3A%2F%2Fehall.njmu.edu.cn%2Fnew%2Findex.html'
        headers1 = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 Edg/92.0.902.67'}
        r = self.session.get(url1, headers=headers1)
        r.encoding = 'utf-8'
        html = r.text
        lt = re.findall('name="lt" value="(.*)"', html)[0]
        key = re.findall('id="pwdDefaultEncryptSalt" value="(.*?)"', html)[0]
        pwd = AESEncrypt(password, key)  # AES密码加密
        execution = re.findall('name="execution" value="(.*?)"', html)[0]
        data = {'username': username,
                'password': pwd,
                'lt': lt,
                'dllt': 'userNamePasswordLogin',
                'execution': execution,
                '_eventId': 'submit',
                'rmShown': '1'}
        headers2 = self.headers.update({'Host': 'authserver.njmu.edu.cn',
                                        'Referer': 'http://authserver.njmu.edu.cn/authserver/login?service=http%3A%2F%2Fehall.njmu.edu.cn%2Flogin%3Fservice%3Dhttp%3A%2F%2Fehall.njmu.edu.cn%2Fnew%2Findex.html'})
        res1 = self.session.post(url1, headers=headers2, data=data, allow_redirects=False)  # post请求
        if res1.status_code != 302:
            raise LoginError
        location = res1.headers["Location"]
        headers3 = self.headers.update({'Host': 'http://authserver.njmu.edu.cn/',
                                        'Referer': 'http://authserver.njmu.edu.cn/'})
        res2 = self.session.get(location, headers=headers3, allow_redirects=False)  # get请求 302
        location = res2.headers["Location"]
        headers4 = self.headers.update({'Host': 'ehall.njmu.edu.cn',
                                        'Referer': 'http://authserver.njmu.edu.cn/'})
        self.session.get(location, headers=headers4, allow_redirects=False)  # get请求 200，此三部完成网上办事大厅的登录
        # 健康打卡
        amp = '6276111169665617'  # 教务的amp
        destination = 'http://ehall.njmu.edu.cn/appShow?appId={}&_={}'.format(amp, int(time.time()))
        headers5 = self.headers.update({'Host': 'ehall.njmu.edu.cn',
                                        'Referer': 'http://ehall.njmu.edu.cn/new/index.html'})
        res4 = self.session.get(destination, headers=headers5, allow_redirects=False)
        location = res4.headers["Location"]
        self.session.get(location, headers=headers5)
        cookies_dict = requests.utils.dict_from_cookiejar(self.session.cookies)
        return cookies_dict


class Mail:
    def __init__(self, dic):
        self.dic = dic

    def send(self):  # 发送邮件
        with open('ID.yaml', 'r', encoding='utf-8') as f:
            mail = yaml.load(f.read())['mail']
        sender = mail['sender']
        password = mail['password']
        receivers = mail['receivers']
        smtp_server = mail['smtp_server']
        mail_msg = self.dic['info']
        message = MIMEText(mail_msg, 'html', 'utf-8')
        message['From'] = Header(self.dic['From'], 'utf-8')
        message['To'] = Header(self.dic['To'], 'utf-8')
        message['Subject'] = Header(self.dic['subject'], 'utf-8')
        server = smtplib.SMTP_SSL(smtp_server)
        server.connect(smtp_server, port=994)
        server.login(sender, password)
        server.sendmail(sender, receivers, message.as_string())
        server.quit()
