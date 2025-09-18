import json
import time
import pandas as pd

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
df = pd.read_excel(resource_path("./batch_list/微型校园接收机_favorite_1.xlsx"))
private_videos = df[df["title"].str.contains("Pre", na=False)]
print(private_videos)

