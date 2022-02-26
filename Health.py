import datetime
import re
import requests
import json
import random
from common import SchoolLogin, Mail
from datetime import datetime
import yaml


class InfoException(BaseException):
    """信息更改异常"""
    pass


class PostInfo(object):  # 提交函数，用于提交打卡信息
    def __init__(self):
        self.result = ''
        self.info = ''
        with open('ID.yaml', 'r') as f:
            Id = yaml.load(f.read(), Loader=yaml.FullLoader)['id']
        self.username = Id['username']
        s = SchoolLogin(Id)
        s.main_login()
        self.cookie = s.health()
        self.FinalUrl = 'http://ehall.njmu.edu.cn/qljfwappnew/sys/lwWiseduHealthInfoDailyClock/modules/healthClock/T_HEALTH_DAILY_INFO_SAVE.do'
        self.dict = {}  # 该字典从旧提交信息中获取数据，并合并新构造的日期，为最终的提交参数

    def get_old_info(self):  # 从文件中获取旧数据，旧数据由浏览器post请求获取
        with open('疫情打卡提交信息.txt', 'r', encoding='utf-8') as f:
            strings = f.readlines()
        KeyInfo = []
        ValueInfo = []
        for string in strings:
            string = string.replace('/n', '')
            ValueInfo.append(re.findall(r'(?<=: ).*', string)[0])
            KeyInfo.append(re.findall(r'.*(?=: )', string)[0])
            self.dict = dict(zip(KeyInfo, ValueInfo))

    def time_create(self):  # 创造提交时间
        t = datetime.now()
        date1 = t.strftime("%Y-%m-%d")
        wid = date1+'-'+self.username
        CZRQ = t.strftime("%Y-%m-%d %H:%M:%S")
        s1 = random.randint(1, 59)
        s2 = random.randint(1, 59)
        m1 = random.randint(1, 5)
        Ftime1 = ' 08:{:0>2}:{:0>2}'.format(m1, s1)
        Ftime2 = ' 08:{:0>2}:{:0>2}'.format(m1 + 2, s2)
        CREATED_AT = date1 + Ftime2
        FILL_TIME = date1 + Ftime1
        return [CZRQ, CREATED_AT, FILL_TIME, date1, wid]

    def combine(self):  # 参数整合，形成最终提交的self.dict
        ltime = self.time_create()  # 创造提交时间
        self.get_old_info()  # 获取旧的提交数据
        CZRQ = ltime[0]
        CREATED_AT = ltime[1]
        FILL_TIME = ltime[2]
        NEED_CHECKIN_DATE = ltime[3]
        WID = ltime[4]
        self.dict['WID'] = WID
        self.dict['CZRQ'] = CZRQ
        self.dict['CREATED_AT'] = CREATED_AT
        self.dict['FILL_TIME'] = FILL_TIME
        self.dict['NEED_CHECKIN_DATE'] = NEED_CHECKIN_DATE

    def new_query(self):  # 此函数用于查询是否有新的url指向，返回的是今天需要提交的问题
        url1 = 'http://ehall.njmu.edu.cn/qljfwappnew/sys/lwWiseduHealthInfoDailyClock/modules/healthClock.do'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.62'}
        params = {'*json': '1'}
        p = requests.post(url1, headers=headers, cookies=self.cookie, params=params)
        dict1 = json.loads(p.text)
        InfoSave = dict1['models'][1]
        if InfoSave['modelName'] != 'T_HEALTH_DAILY_INFO':
            raise InfoException
        else:
            new_dict = {}
            list1 = InfoSave['params']
            for i in list1:
                new_dict[i['name']] = i['caption']
            return new_dict

    def check(self):  # 此函数用于查询是否有新的问题，采用方法是新的问题是否包含在旧的字典之中
        new_dict = self.new_query()
        new_query = set(new_dict.keys())
        old_query = set(self.dict.keys())
        if new_query - old_query != set():
            self.info = '出现新的问题{}'.format(new_query - old_query)
            # print('出现新的问题{}'.format(new_query - old_query))
            raise InfoException
        else:
            self.check_info()
            print('无信息更改')

    def assert_dict(self, given, result):  # 此函数用于判读given字典是否包含在result字典之中
        for key in given:
            if (key in result) & (result[key] == given[key]):
                continue
            else:
                # print('{}不在{}之中'.format(given,result))
                self.info = '信息已发生更改，{}不在{}之中'.format(given, result)
                raise InfoException

    def check_info(self):  # 此函数用于查询旧的选项是否在今日的选项之中
        lurl = ['http://ehall.njmu.edu.cn/qljfwappnew/code/604790c7-c5d9-487e-a38a-83bb3baa8092/TODAY_SITUATION.do',
                'http://ehall.njmu.edu.cn/qljfwappnew/code/604790c7-c5d9-487e-a38a-83bb3baa8092/TODAY_CONDITION.do',
                'http://ehall.njmu.edu.cn/qljfwappnew/code/604790c7-c5d9-487e-a38a-83bb3baa8092/TODAY_NAT_CONDITION.do',
                'http://ehall.njmu.edu.cn/qljfwappnew/code/604790c7-c5d9-487e-a38a-83bb3baa8092/TODAY_VACCINE_CONDITION.do',
                'http://ehall.njmu.edu.cn/qljfwappnew/code/604790c7-c5d9-487e-a38a-83bb3baa8092/TODAY_BODY_CONDITION.do',
                'http://ehall.njmu.edu.cn/qljfwappnew/code/604790c7-c5d9-487e-a38a-83bb3baa8092/TODAY_HEALTH_CODE.do',
                'http://ehall.njmu.edu.cn/qljfwappnew/code/604790c7-c5d9-487e-a38a-83bb3baa8092/CONTACT_HISTORY.do',
                'http://ehall.njmu.edu.cn/qljfwappnew/code/604790c7-c5d9-487e-a38a-83bb3baa8092/TODAY_ISOLATE_CONDITION.do',
                'http://ehall.njmu.edu.cn/qljfwappnew/code/604790c7-c5d9-487e-a38a-83bb3baa8092/TODAY_TARRY_CONDITION.do',
                'http://ehall.njmu.edu.cn/qljfwappnew/code/604790c7-c5d9-487e-a38a-83bb3baa8092/BY1.do']
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.62',
            'Referer': 'http://ehall.njmu.edu.cn/qljfwappnew/sys/lwWiseduHealthInfoDailyClock/index.do?amp_sec_version_=1&gid_=VE5MMnl0UndHbGJybG1zbEdpTCsyV0cyZDM0bGJFbzFEN2t4RGpSZ04vemFKQ2NFSllkSHVKWkhYQVN5UEdwTnNrcldkVnQ3NWV6dW1rNHlLaTByR0E9PQ&EMAP_LANG=zh&THEME=teal'}
        for url in lurl:
            p = requests.post(url, headers=headers, cookies=self.cookie)
            dict1 = json.loads(p.text)
            list1 = dict1['datas']['code']['rows']
            dict2 = {}
            for eachdict in list1:
                dict2[eachdict['id']] = eachdict['name']
            target = re.findall('(?<=604790c7-c5d9-487e-a38a-83bb3baa8092/).*?(?=\.do)', url)[
                0]  # 此正则表达式用于获取url链接中如TODAY_SITUATION的部分
            target_situation = target + '_DISPLAY'
            dict3 = {self.dict[target]: self.dict[target_situation]}
            self.assert_dict(dict3, dict2)

    def main(self):  # 执行函数
        try:
            self.combine()
            self.check()
        except InfoException:
            self.result = 'Fail'
        else:
            url = 'http://ehall.njmu.edu.cn/qljfwappnew/sys/lwWiseduHealthInfoDailyClock/modules/healthClock/T_HEALTH_DAILY_INFO_SAVE.do'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.62'}
            p = requests.post(url, headers=headers, cookies=self.cookie, params=self.dict)
            self.result = 'Success'
            self.info = '今日打卡成功'
        finally:
            self.mail_sender()

    def mail_sender(self):  # 发送邮件
        mail_msg = """
        <p>{}</p>
        """.format(self.info)
        dic = {'From':'健康打卡','To':'通知','info':mail_msg,'subject': self.result}
        s = Mail(dic)


c = PostInfo()
c.main()
