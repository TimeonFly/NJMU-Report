from common import SchoolLogin
import requests
import json


class GetInfo(object):
    def __init__(self):
        self.wid = None
        self.cookie = None
        self.username = None
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Origin': 'http://authserver.njmu.edu.cn',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.84'}

    def login(self):
        s = SchoolLogin()
        self.cookie = s.main_login()

    def get_info(self):
        get_url = 'http://ehall.njmu.edu.cn/qljfwappnew/sys/lwWiseduHealthInfoDailyClock/modules/healthClock/getMyDailyReportDatas.do'
        headers1 = {'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                    'Connection': 'keep-alive',
                    'Host': 'ehall.njmu.edu.cn',
                    'Origin': 'http://ehall.njmu.edu.cn',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.84',
                    'Referer': 'http://ehall.njmu.edu.cn/qljfwappnew/sys/lwWiseduHealthInfoDailyClock/index.do?amp_sec_version_=1&gid_=YmliV2M2Skp0Z1BjV2RBVkl4YjZIMGZzSG5DSFdjMllLWnZuVVU3SkFxU0V0TUtkT0NRVUR1UDd6VnpQREd3N1hpN2RVQkNkblNmNFpzNE5ZM3BPQnc9PQ&EMAP_LANG=zh&THEME=golden'}
        data = {'pageNumber': '1',
                'pageSize': '10'}
        r = requests.post(get_url, headers=headers1, cookies=self.cookie, data=data)
        info_dict = json.loads(r.text)['datas']['getMyDailyReportDatas']['rows'][0]
        return info_dict

    @staticmethod
    def parse(info_dict):
        info_dict.update({'CREATED_AT': '',
                          'CZRQ': '',
                          'FILL_TIME': '',
                          'NEED_CHECKIN_DATE': '',
                          'WID': ''})
        with open('疫情打卡提交信息.txt', 'w+', encoding='utf-8') as f:
            for i in info_dict.keys():
                if info_dict[i] is None:
                    line = i + ': '
                else:
                    line = i + ': ' + info_dict[i]
                print(line, file=f)

    def main(self):
        self.login()
        info_dict = self.get_info()
        self.parse(info_dict)


G = GetInfo()
G.main()
