import requests
import pandas as pd
from bs4 import BeautifulSoup
import os

# 发送HTTP请求获取网页内容
url = "https://proxymist.com/zh/countries/asia/china/"

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
    data = scrape_table_data(url)
    df = pd.DataFrame(data,columns=['IP', 'PORT', 'PROTOCOL', 'ANONYMITY', 'REGION','OPERATOR','DELAY','SPEED','RUN_STATE','LAST_CHECK'])
    df = df.dropna()
    if os.path.exists('./app_config'):
        df.to_csv('./app_config/proxy_ip_china.csv', index=False)
    else:
        os.mkdir('./app_config')
        df.to_csv('./app_config/proxy_ip_china.csv', index=False)