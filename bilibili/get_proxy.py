import requests
import pandas as pd
from bs4 import BeautifulSoup
import os
from utils import resource_path

# 发送HTTP请求获取网页内容
origin_url = "https://proxymist.com/zh/countries/asia/china/"
new_http_url = "https://www.proxy-list.download/api/v1/get?type=http"
new_https_url = "https://www.proxy-list.download/api/v1/get?type=https"

def scrape_table_data(url):

    try:
        # 设置请求头，模拟浏览器访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'content-type': 'application / javascript'
        }

        # 发送请求
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        response.raise_for_status()  # 检查请求是否成功

        # 解析网页内容
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find("table")


        if table:
            # 提取表格数据
            data = []
            rows = table.find_all("tr")
            # print(f"表格大小：{str(rows.__sizeof__())}")
            for row in rows:
                cols = row.find_all("td")
                cols = [col.text.strip() for col in cols]
                data.append(cols)
            return data
        else:
            print("未找到代理IP表格数据")
            return None

    except requests.RequestException as e:
        print(f"请求错误: {e}")
        return None
    except ValueError as e:
        print(f"解析错误: {e}")
        return None

def create_proxies_table_csv():
    data = scrape_table_data(origin_url)
    df = pd.DataFrame(data,columns=['IP', 'PORT', 'PROTOCOL', 'ANONYMITY', 'REGION','OPERATOR','DELAY','SPEED','RUN_STATE','LAST_CHECK'])
    df = df.dropna()
    if os.path.exists(resource_path('./app_config')):
        df.to_csv(resource_path('./app_config/proxy_ip_china.csv'), index=False)
    else:
        os.mkdir(resource_path('./app_config'))
        df.to_csv(resource_path('./app_config/proxy_ip_china.csv'), index=False)

def create_proxies_list(protocol):
    # 设置请求头，模拟浏览器访问
    if protocol == 'http':
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'content-type': 'application/javascript',
            'Referer' : new_http_url
        }
    else:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'content-type': 'application/javascript',
            'Referer' : new_https_url
        }
    response = requests.get(new_http_url, headers=headers)
    proxy_list = []
    for line in response.text.split('\r\n'):
        if line != '' and line is not None:
            line = line.split(':')
            line = line[0] + ':' + line[1]
            proxy_list.append(line)
    return proxy_list

# print(create_proxies_list('http'))