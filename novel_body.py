import requests
from pyquery import PyQuery as pq
from pymysql import Connection


class Novelbody(object):
    def __init__(self,url,headers):
        self.url = url
        self.headers = headers


    def get_novel_body(self):
        response = requests.request("GET", self.url, headers=self.headers)

        response.encoding = 'gbk'

        if response.status_code == 200:
            doc = pq(response.text)
            tag = doc('div')
            origin_body = tag.text()

            start_index = origin_body.find("loadAdv(2, 0);")
            end_index = origin_body.find("loadAdv(3, 0);")

            # 如果找到了 label2 和 label3
            if start_index != -1 and end_index != -1:
                # 提取 label2 和 label3 之间的内容
                desired_content = origin_body[start_index + len("loadAdv(2, 0);"):end_index].strip()

            else:
                start_index = origin_body.find("loadAdv(2,0);")
                end_index = origin_body.find("loadAdv(3,0);")
                desired_content = origin_body[start_index + len("loadAdv(2,0);"):end_index].strip()
            return desired_content
        else:
            return null


if __name__ == "__main__":
    url = "https://www.69xinshu.com/txt/49986/32971978"

    headers = {
        'authority': 'cdn.shucdn.com',
        'accept': 'text/css,*/*;q=0.1',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'referer': 'https://www.69xinshu.com/',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'style',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    conn = Connection(
        host='localhost',
        port=3306,
        user='root',
        password='xq200431',
        autocommit=True
    )
    cursor = conn.cursor()  # 获取游标对象
    conn.select_db("novels")

    novel = Novelbody(url,headers)
    body = novel.get_novel_body()

    print(body)