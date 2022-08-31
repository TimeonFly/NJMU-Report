import datetime
import re
import requests
import json
import random
import sys
from common import SchoolLogin, Mail, LoginError, get_info
from datetime import datetime, timezone, timedelta


def get_time_str():
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    bj_dt = utc_dt.astimezone(timezone(timedelta(hours=8)))
    return bj_dt.strftime("%Y-%m-%d %H:%M:%S")


def log(content):
    print(get_time_str() + ' ' + str(content))
    sys.stdout.flush()


class InfoException(Exception):
    """信息异常"""

    def __init__(self, info):
        log(info)


class TimeException(Exception):
    """时间异常"""

    def __init__(self, info):
        log(info)


class PostInfo(object):  # 提交函数，用于提交打卡信息

    def __init__(self):
        self.result = ''
        self.info = ''
        self.cookie = None
        self.dict = {}  # 该字典从旧提交信息中获取数据，并合并新构造的日期，为最终的提交参数

    def get_wid(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.62'}
        url = 'http://ehall.njmu.edu.cn/qljfwappnew/sys/lwWiseduHealthInfoDailyClock/modules/healthClock/getMyTodayReportWid.do'
        params = {'pageNumber': '1'}
        p = requests.post(url, headers=headers, cookies=self.cookie, params=params)
        try:
            info_dict = json.loads(p.text)['datas']['getMyTodayReportWid']['rows'][0]
        except IndexError:
            self.info = 'WID参数获取失败，请稍后再尝试...'
            raise InfoException(self.info)
        else:
            return info_dict

    def get_old_info(self):  # 从文件中获取旧数据，旧数据由浏览器post请求获取
        with open('疫情打卡提交信息.txt', 'r', encoding='utf-8') as f:
            strings = f.readlines()
        key_info = []
        value_info = []
        for string in strings:
            string = string.replace('/n', '')
            try:
                value_info.append(re.findall(r'(?<=: ).*', string)[0])
                key_info.append(re.findall(r'.*(?=: )', string)[0])
            except IndexError:
                value_info.append('')
                key_info.append(re.findall(r'.*(?=:)', string)[0])
            finally:
                self.dict.update(dict(zip(key_info, value_info)))

    def create_info(self):  # 参数整合，形成最终提交的self.dict
        wid_dict = self.get_wid()
        wid = wid_dict['WID']
        t = datetime.now()
        if t.hour >= 11:
            t = t.replace(hour=random.randint(7, 10))
        date1 = t.strftime("%Y-%m-%d")
        czrq = t.strftime("%Y-%m-%d %H:%M:%S")
        created_at = t + timedelta(seconds=-1)
        created_at = created_at.strftime('%Y-%m-%d %H:%M:%S')
        fill_time = t + timedelta(minutes=-2, seconds=random.randint(-59, -1))
        fill_time = fill_time.strftime('%Y-%m-%d %H:%M:%S')
        self.dict['WID'] = wid
        self.dict['CZRQ'] = czrq
        self.dict['CREATED_AT'] = created_at
        self.dict['FILL_TIME'] = fill_time
        self.dict['NEED_CHECKIN_DATE'] = date1

    def check_question(self):  # 此函数用于查询是否有新的问题，采用方法是新的问题是否包含在旧的字典之中
        new_dict = self.get_wid()
        new_query = set(new_dict.keys())
        old_query = set(self.dict.keys())
        dif_set = new_query - old_query
        if dif_set != set():
            dif_dic = {i: new_dict[i] for i in dif_set}
            self.info = '出现新的问题{}'.format(dif_dic)
            raise InfoException(self.info)
        else:
            self.check_info()

    def assert_dict(self, given, result):  # 此函数用于判读given字典是否包含在result字典之中
        set1 = set(given.items())
        set2 = set(result.items())
        if not set1.issubset(set2):  # 将字典转换成集合以后，判断旧数据是否是新数据的子集，采用的是issubset()函数
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
            dict2 = {i['id']: i['name'] for i in list1}
            dict2.update({'': ''})
            target_situation = target + '_DISPLAY'
            dict3 = {self.dict[target]: self.dict[target_situation]}
            self.assert_dict(dict3, dict2)

    def confirm(self):  # 此函数用于确认今天是否打卡过，方法是检查健康打卡页面是否有今天打卡的日期，调用的是common模块里的get_info函数
        info = get_info(self.cookie)
        date = info['NEED_CHECKIN_DATE']
        t = datetime.now()
        date1 = t.strftime("%Y-%m-%d")
        if date == date1:
            pass
        else:
            self.info = '出现错误，今日打卡失败！'
            raise InfoException(self.info)

    def mail_send(self):  # 发送邮件
        mail_msg = """
        <p>{}</p>
        """.format(self.info)
        dic = {'From': '健康打卡', 'To': '通知', 'info': mail_msg, 'subject': self.result}
        m = Mail(dic)
        m.send()

    def main(self):  # 执行函数
        try:
            s = SchoolLogin()
            self.cookie = s.main_login()
            self.get_old_info()  # 获取旧的提交数据
            self.check_question()
            self.create_info()
        except InfoException:
            self.result = 'Fail'
        except TimeException:
            self.result = 'Fail'
            log('您输入的时间有错误，请检查ID.yaml文件中的time配置！')
        except LoginError:
            self.result = 'Fail'
            self.info = '账号或密码错误，登录失败'
            log(self.info)
        else:
            url = 'http://ehall.njmu.edu.cn/qljfwappnew/sys/lwWiseduHealthInfoDailyClock/modules/healthClock/T_HEALTH_DAILY_INFO_SAVE.do'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.62'}
            requests.post(url, headers=headers, cookies=self.cookie, params=self.dict)
            self.result = 'Success'
            self.info = '今日打卡成功'
            t = datetime.now()
            log(t.strftime('%m-%d') + '打卡成功')
        finally:
            self.confirm()
            self.mail_send()


def main_handler(event, context):
    log('脚本开始执行...')
    c = PostInfo()
    c.main()


if __name__ == '__main__':
    main_handler(None, None)
