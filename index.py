import datetime
import re
import requests
import json
import random
import sys
from common import SchoolLogin, Mail
from datetime import datetime, timezone, timedelta
import yaml


def get_time_str():
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    bj_dt = utc_dt.astimezone(timezone(timedelta(hours=8)))
    return bj_dt.strftime("%Y-%m-%d %H:%M:%S")


def log(content):
    print(get_time_str() + ' ' + str(content))
    sys.stdout.flush()


class InfoException(Exception):
    """信息更改异常"""
    def __init__(self, info):
        log(info)


class PostInfo(object):  # 提交函数，用于提交打卡信息
    def __init__(self):
        self.result = ''
        self.info = ''
        with open('ID.yaml', 'r', encoding='utf-8') as f:
            bs_id = yaml.load(f.read())['id']
        self.username = bs_id['username']
        s = SchoolLogin(bs_id)
        self.cookie = s.main_login()
        self.dict = {}  # 该字典从旧提交信息中获取数据，并合并新构造的日期，为最终的提交参数

    def get_old_info(self):  # 从文件中获取旧数据，旧数据由浏览器post请求获取
        with open('疫情打卡提交信息.txt', 'r', encoding='utf-8') as f:
            strings = f.readlines()
        key_info = []
        value_info = []
        for string in strings:
            string = string.replace('/n', '')
            value_info.append(re.findall(r'(?<=: ).*', string)[0])
            key_info.append(re.findall(r'.*(?=: )', string)[0])
            self.dict = dict(zip(key_info, value_info))

    def create_info(self):  # 参数整合，形成最终提交的self.dict
        t = datetime.now()
        date1 = t.strftime("%Y-%m-%d")
        wid = date1 + '-' + self.username
        czrq = t.strftime("%Y-%m-%d %H:%M:%S")
        s1, s2 = random.sample(range(1, 59), 2)
        m1 = random.randint(1, 5)
        ftime1 = ' 08:{:0>2}:{:0>2}'.format(m1, s1)
        ftime2 = ' 08:{:0>2}:{:0>2}'.format(m1 + 2, s2)
        created_at = date1 + ftime2
        fill_time = date1 + ftime1
        self.dict['WID'] = wid
        self.dict['CZRQ'] = czrq
        self.dict['CREATED_AT'] = created_at
        self.dict['FILL_TIME'] = fill_time
        self.dict['NEED_CHECKIN_DATE'] = date1

    def new_query(self):  # 此函数用于查询是否有新的url指向，返回的是今天需要提交的问题
        url1 = 'http://ehall.njmu.edu.cn/qljfwappnew/sys/lwWiseduHealthInfoDailyClock/modules/healthClock.do'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.62'}
        params = {'*json': '1'}
        p = requests.post(url1, headers=headers, cookies=self.cookie, params=params)
        dict1 = json.loads(p.text)
        info_save = dict1['models'][1]
        if info_save['modelName'] != 'T_HEALTH_DAILY_INFO':
            raise InfoException('modelName已更改')
        else:
            new_dict = {}
            list1 = info_save['params']
            for i in list1:
                new_dict[i['name']] = i['caption']
            return new_dict

    def check(self):  # 此函数用于查询是否有新的问题，采用方法是新的问题是否包含在旧的字典之中
        new_dict = self.new_query()
        new_query = set(new_dict.keys())
        old_query = set(self.dict.keys())
        if new_query - old_query != set():
            self.info = '出现新的问题{}'.format(new_query - old_query)
            raise InfoException(self.info)
        else:
            self.check_info()

    def assert_dict(self, given, result):  # 此函数用于判读given字典是否包含在result字典之中
        for key in given:
            if (key in result) & (result[key] == given[key]):
                continue
            else:
                # print('{}不在{}之中'.format(given,result))
                self.info = '信息已发生更改，{}不在{}之中'.format(given, result)
                raise InfoException(self.info)

    def check_info(self):  # 此函数用于查询旧的选项是否在今日的选项之中
        target_list = ['TODAY_SITUATION',
                       'TODAY_CONDITION',
                       'TODAY_NAT_CONDITION',
                       'TODAY_VACCINE_CONDITION',
                       'TODAY_BODY_CONDITION',
                       'TODAY_HEALTH_CODE',
                       'CONTACT_HISTORY',
                       'TODAY_ISOLATE_CONDITION',
                       'TODAY_TARRY_CONDITION',
                       'BY1']
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.62',
            'Referer': 'http://ehall.njmu.edu.cn/qljfwappnew/sys/lwWiseduHealthInfoDailyClock/index.do?amp_sec_version_=1&gid_=VE5MMnl0UndHbGJybG1zbEdpTCsyV0cyZDM0bGJFbzFEN2t4RGpSZ04vemFKQ2NFSllkSHVKWkhYQVN5UEdwTnNrcldkVnQ3NWV6dW1rNHlLaTByR0E9PQ&EMAP_LANG=zh&THEME=teal'}
        for target in target_list:
            url = 'http://ehall.njmu.edu.cn/qljfwappnew/code/604790c7-c5d9-487e-a38a-83bb3baa8092/'
            target_url = url + target + '.do'
            p = requests.post(target_url, headers=headers, cookies=self.cookie)
            dict1 = json.loads(p.text)
            list1 = dict1['datas']['code']['rows']
            dict2 = {}
            for each_dict in list1:
                dict2[each_dict['id']] = each_dict['name']
            target_situation = target + '_DISPLAY'
            dict3 = {self.dict[target]: self.dict[target_situation]}
            self.assert_dict(dict3, dict2)

    def mail_sender(self):  # 发送邮件
        mail_msg = """
        <p>{}</p>
        """.format(self.info)
        dic = {'From': '健康打卡', 'To': '通知', 'info': mail_msg, 'subject': self.result}
        Mail(dic)

    def main(self):  # 执行函数
        try:
            self.get_old_info()  # 获取旧的提交数据
            self.create_info()
            self.check()
        except InfoException:
            self.result = 'Fail'
        else:
            url = 'http://ehall.njmu.edu.cn/qljfwappnew/sys/lwWiseduHealthInfoDailyClock/modules/healthClock/T_HEALTH_DAILY_INFO_SAVE.do'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.62'}
            requests.post(url, headers=headers, cookies=self.cookie, params=self.dict)
            self.result = 'Success'
            self.info = '今日打卡成功'
            t = datetime.now()
            log(t.strftime('%m-%d')+'打卡成功')
        finally:
            self.mail_sender()


def main_handler(event, context):
    log('脚本开始执行...')
    c = PostInfo()
    c.main()


main_handler(None, None)
