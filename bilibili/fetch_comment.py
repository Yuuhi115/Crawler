import requests
import json
from utils import *
import os
import time
import pandas as pd
import re
from lxml import html


def extract_BV(video_url):
    # 使用正则表达式提取 BV 号
    match = re.search(r"\/(BV[^\/]*)\/", video_url)
    if match:
        bv_number = match.group(1)
        return bv_number
    else:
        return None


def run_comment_crawler(video_url):
    if os.path.exists(resource_path("./app_config/cookies.json")):
        cookie = get_cookies_string()
        headers = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0',
            "Referer": video_url,
            "Cookie": cookie
        }
    else:
        headers = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0',
            "Referer": video_url
        }
    oid = extract_BV(video_url)
    if oid is None:
        print("请输入正确的视频链接")
        return False

    r_page = 1
    limit_page = read_properties_from_config("comment_max_pages")
    root_path = read_properties_from_config("export_dir")

    proxy_enabled = read_properties_from_config("proxy_enabled")
    proxy_ip = read_properties_from_config("proxy_ip")
    proxy_port = read_properties_from_config("proxy_port")

    sub_comment_enabled = read_properties_from_config("fetch_sub_comments")

    if proxy_enabled == "true":
        proxy_url = f"http://{proxy_ip}:{proxy_port}"
        proxies = {
            "http": proxy_url,
            "https": proxy_url
        }
        print(f"代理已启用，代理地址：{proxy_url}")
    else:
        proxies = None
    if '@-@' in root_path:
        root_path = root_path.replace('@-@', ':')
    if "www.bilibili.com/video/BV" in video_url:
        type = "video"
    elif "www.bilibili.com/bangumi/play/ep" in video_url:
        type = "anime"
    else:
        type = "charge"
    video_title = get_video_title(video_url, headers, type)
    file_path = f"{root_path}/{video_title}/comments"
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    # 初始化空的 DataFrame
    comments_df = pd.DataFrame(columns=['comment_id', 'user', 'comment_content', 'like', 'reply_count'])
    sub_comments_df = pd.DataFrame(columns=['comment_id','root_comment_id', 'user', 'comment_content', 'like'])
    time.sleep(1)
    while True:
        if r_page > int(limit_page):
            # print(f"r_page:{r_page}")
            sub_comments_df.to_excel(resource_path(f"{file_path}/sub_comments.xlsx"), index=False)
            comments_df.to_excel(resource_path(f"{file_path}/comments.xlsx"), index=False)
            print(f"评论已保存至 {resource_path(f'{file_path}/comments.xlsx')}")
            return True
        root_comment_url = f'https://api.bilibili.com/x/v2/reply/main?next={r_page}&type=1&oid={oid}&mode=3'
        try:
            if proxy_enabled == "true":
                response = requests.get(root_comment_url, headers=headers, proxies=proxies, timeout=10)
            else:
                response = requests.get(root_comment_url, headers=headers)
            comment_source = json.loads(response.text)
            comment_list = comment_source["data"]["replies"]
            video_id = comment_list[0]["oid"]
            if len(comment_list) == 0:
                sub_comments_df.to_excel(resource_path(f"{file_path}/sub_comments.xlsx"), index=False)
                comments_df.to_excel(resource_path(f"{file_path}/comments.xlsx"), index=False)
                print(f"评论已保存至 {resource_path(f'{file_path}/comments.xlsx')}")
                return True
            print(f"正在爬取第{r_page}页评论...")
            for comment in comment_list:
                comment_id = str(comment["rpid"])
                comment_content = comment["content"]["message"]
                user = comment["member"]["uname"]
                like = comment["like"]
                reply = comment["rcount"]
                # 将数据添加到 DataFrame
                new_row = pd.DataFrame({
                    'comment_id': [comment_id],
                    'user': [user],
                    'comment_content': [comment_content],
                    'like': [like],
                    'reply_count': [reply]
                })
                if sub_comment_enabled == "true" and reply > 0:
                    time.sleep(1)
                    print(f"正在爬取评论id:{comment_id}的子评论...")
                    sub_comments_df = get_sub_comments(video_id, comment_id, reply, headers, sub_comments_df, proxies)
                comments_df = pd.concat([comments_df, new_row], ignore_index=True)
            r_page += 1
            time.sleep(1)
            if comments_df.empty:
                print("未获取到评论")
        except json.JSONDecodeError as e:
            print(f"JSON 解析失败: {e}")
            if comments_df.empty:
                print("未获取到评论")
            else:
                sub_comments_df.to_excel(resource_path(f"{file_path}/sub_comments.xlsx"), index=False)
                comments_df.to_excel(resource_path(f"{file_path}/comments.xlsx"), index=False)
                print(f"评论已保存至 {resource_path(f'{file_path}/comments.xlsx')}")
            return False


def get_video_title(video_url, headers, type):
    response = requests.get(video_url, headers=headers)
    tree = html.fromstring(response.text)
    # 获取视频标题信息
    title = tree.xpath('/html/head/title')
    title_text = ""
    if type == "video" or type == "charge":
        title_parts = title[0].text.split("_")
        if len(title_parts) > 2:
            title_text = "_".join(title_parts[:-2])  # 去除最后两个元素后，用下划线连接
        else:
            title_text = title_parts[0]
    elif type == "anime":
        title_text = title[0].text.split("-")[0]
    # 替换Windows系统不允许的字符
    title_text = re.sub(r'[\\/:*?"<>|“”×]', '_', title_text)
    # logger.info(f"视频标题：{title_text}")
    print(f"视频标题：{title_text}")
    return title_text

def get_sub_comments(video_id, comment_id, length, headers, sub_comments_df, proxies = None):
    page_num = int(length / 10) + 1
    try:
        for current_page in range(1, int(page_num) + 1):
            reply_url = f"https://api.bilibili.com/x/v2/reply/reply?oid={video_id}&type=1&root={comment_id}&ps=10&pn={current_page}&web_location=333.788"
            response = requests.get(reply_url, headers=headers, proxies=proxies, timeout=10)
            comment_source = json.loads(response.text)
            comment_list = comment_source["data"]["replies"]
            for comment in comment_list:
                root_comment_id = str(comment["root"])
                comment_content = comment["content"]["message"]
                user = comment["member"]["uname"]
                like = comment["like"]
                new_row = pd.DataFrame({
                    'comment_id': [comment_id],
                    'root_comment_id': [root_comment_id],
                    'user': [user],
                    'comment_content': [comment_content],
                    'like': [like]
                })
                sub_comments_df = pd.concat([sub_comments_df, new_row], ignore_index=True)
            time.sleep(1)
        return sub_comments_df
    except requests.exceptions.RequestException as e:
        print(f"子评论请求失败: {e}")
        return sub_comments_df
    except json.JSONDecodeError as e:
        print(f"子评论JSON解析失败: {e}")
        return sub_comments_df

