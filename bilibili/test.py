import json
import time
from http.client import responses

import pandas as pd
import requests

from utils import *
from fetch_site import run_favorite_category
# 读取并添加cookie
# with open("./app_config/cookies.json", "r") as f:
#     cookies = json.load(f)
#
# cookies_str = ""
# for cookie in cookies:
#     cookies_str += cookie["name"] + "=" + cookie["value"] + "; "
#
# print(cookies_str)

# print(get_cookies_expiry_info())
# def test():
#     cookies = get_cookies_expiry_info_formatted()
#     cookie = [cookie for cookie in cookies if cookie.get("name") == "SESSDATA"]
#     return cookie[0]
#
# cookie = test()
# print(cookie["expiry_timestamp"], cookie["expiry_date"], cookie["name"])
# print(int(time.time()))
# print(f"cookie有效期: {int((cookie["expiry_timestamp"] - time.time()) / 86400)} 天")
# print(get_remain_time("SESSDATA"))

# print(load_proxy_list("../proxy_ip/", "proxy_ip_china.csv"))
#
# for i in range(1,3):
#     print(i)

# print(get_cookie_by_name("DedeUserID").get("value"))
# print(run_favorite_category())
# df = pd.read_excel(resource_path("./batch_list/微型校园接收机_favorite_1.xlsx"))
# private_videos = df[df["title"].str.contains("Pre", na=False)]
# print(private_videos)
cookie = get_cookies_string()
video_url = "https://www.bilibili.com/video/BV1qkpfzMEqY/?spm_id_from=333.1007.tianma.1-1-1.click&vd_source=07d3ef37851690622a60e79828e5a383"
headers = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0',
            "Referer": video_url,
            "Cookie": cookie
        }

r_page = 2
oid = "115240196901267"
root_comment_url = f'https://api.bilibili.com/x/v2/reply/main?next={r_page}&type=1&oid={oid}&mode=3'
response = requests.get(url=root_comment_url, headers=headers)
comment_source = json.loads(response.text)
with open("root_comment.json", "w", encoding="utf-8") as f:
    json.dump(comment_source, f, ensure_ascii=False, indent=4)

