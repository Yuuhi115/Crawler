import time

import requests
import pandas as pd
from bs4 import BeautifulSoup
import os
import urllib.parse

def get_today_timestamp():
    today = time.localtime()
    date_only = time.strptime(f"{today.tm_year}-{today.tm_mon}-{today.tm_mday}", "%Y-%m-%d")
    today_timestamp = time.mktime(date_only)
    return today_timestamp

def create_request(url, token):
    try:
        # 设置请求头，模拟浏览器访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Content-type': 'application / javascript',
            'Cookie': 'Admin-Token=' + token,
            'Authorization': 'Bearer ' + token
        }

        # 发送请求
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        response.raise_for_status()  # 检查请求是否成功
        return response.json()
        # 解析网页内容
        # soup = BeautifulSoup(response.text, 'html.parser')
        # table = soup.find("table")
        #
        # if table:
        #     # 提取表格数据
        #     data = []
        #     rows = table.find_all("tr")
        #     print(f"表格大小：{str(rows.__sizeof__())}")
        #     for row in rows:
        #         cols = row.find_all("td")
        #         cols = [col.text.strip() for col in cols]
        #         data.append(cols)
        #     return data
        # else:
        #     print("未找到表格数据")
        #     return None

    except requests.RequestException as e:
        print(f"请求错误: {e}")
        return None
    except ValueError as e:
        print(f"解析错误: {e}")
        return None

if __name__ == '__main__':
    base_url = "http://192.168.0.34:8055/prod-api/illegalRecord/record/listjoinWayline?"
    token = 'eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxMzcxMjg3MTkwMyIsImxvZ2luX3VzZXJfa2V5IjoiM2Y4MWJhNjItMzUzYS00MDU1LTljNzgtMjAxZWZkZDY2YjJiIn0.uiW8bijNssY8vL7e6TP-e4qCP3SeFxenyNBI-2ZOUhiRwF-uhnGRE-aq6PnwJ5MKCp2EHi3Gme10NgvWuxiF2Q'
    # response = create_request(base_url, token)
    index = 1
    select_data = []
    break_flag = False
    while True:
        if break_flag:
            break
        print(f"正在爬取第{int(index)}页...")
        # 发送HTTP请求获取网页内容

        data = {
            "pageNum": int(index),
            "pageSize": 10,
            "orderby": "true"
        }
        data = urllib.parse.urlencode(data)
        url = base_url + data
        response = create_request(url, token)  # 获取数据
        # print(response)
        data = response['rows']
        if data:
            for item in data:
                select_time_str = item['timestamp'].split(' ')[0]
                select_time_obj = time.strptime(select_time_str, "%Y-%m-%d")
                select_time = time.mktime(select_time_obj)

                if select_time == get_today_timestamp():
                    select_data.append(item)
                else:
                    break_flag = True
                    break
        index += 1
        time.sleep(1)
    print(f"筛选数据: {select_data}")
    print(f"审核数: {len(select_data)}")

    accept_num = 0
    reject_num = 0
    for item in select_data:
        if item['auditStatus'] == 1:
            accept_num += 1
        elif item['auditStatus'] == -1:
            reject_num += 1

    today = time.localtime()
    date_str = time.strftime("%Y-%m-%d", today)
    print(f"通过数: {accept_num}, 不通过数: {reject_num} 时间: {date_str}")
        # df = pd.DataFrame(data, columns=['IP', 'PORT', 'PROTOCOL', 'ANONYMITY', 'REGION', 'OPERATOR', 'DELAY', 'SPEED',
        #                                  'RUN_STATE', 'LAST_CHECK'])
        # df = df.dropna()
        # if os.path.exists('../proxy_ip'):
        #     df.to_csv('../proxy_ip/proxy_ip_china.csv', index=False)
        # else:
        #     os.mkdir('../proxy_ip')
        #     df.to_csv('../proxy_ip/proxy_ip_china.csv', index=False)
        # print(df)
