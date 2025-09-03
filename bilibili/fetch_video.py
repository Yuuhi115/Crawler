import time
import os
from lxml import html
import json
import requests
import re
from utils import *
from bilibili import *


def run_video_crawler(url, type):
    cookie = None
    if os.path.exists(resource_path("./app_config/cookies.json")):
        cookie = get_cookies_string()
    path = read_properties_from_config("export_dir")
    if '@-@' in path:
        path = path.replace('@-@', ':')
    if cookie != None:
        # logger.info("加载cookies成功")
        print("加载cookies成功")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
            "Cookie": cookie,
            "Referer": url
        }
    else:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
            "Referer": url
        }
    try:
        response = requests.get(url=url, headers=headers)
        tree = html.fromstring(response.text)
        # 获取视频标题信息
        title = tree.xpath('/html/head/title')
        title_text = ""
        if type == "video":
            title_text = title[0].text.split("_")[0]
        elif type == "anime":
            title_text = title[0].text.split("-")[0]
        # 替换Windows系统不允许的字符
        title_text = re.sub(r'[\\/:*?"<>|]', ' ', title_text)
        # logger.info(f"视频标题：{title_text}")
        print(f"视频标题：{title_text}")
        file_path = f"{path}/{title_text}"
        if not os.path.exists(file_path):
            os.makedirs(file_path)
            # logger.info(f"创建目录：{file_path}")
            print(f"创建目录：{file_path}")

        # image_path = f"{file_path}/image"
        # if not os.path.exists(image_path):
        #     os.makedirs(image_path)

        cover_image = tree.xpath('//img[@id="wxwork-share-pic"]/@src')
        # print("封面图片地址：", cover_image[0])
        # download_with_progress(cover_image[0], headers, f"{image_path}/cover.png")
        # 提取视频和源音频源信息
        video_url, audio_url = None, None
        if type == "video":
            video_url, audio_url = get_video_json(tree, file_path)
        elif type == "anime":
            video_url, audio_url = get_anime_json(tree, file_path)
        time.sleep(3)
        # 下载视频
        # logger.info("即将开始下载视频...")
        print("即将开始下载视频...")
        # 下载视频和音频
        if video_url != None and audio_url != None:
            bv_path = f"{file_path}/data"
            if not os.path.exists(bv_path):
                os.makedirs(bv_path)
            download_with_progress(video_url, headers, f"{bv_path}/video.mp4")
            # logger.info("视频下载完成")
            print("视频下载完成")
            time.sleep(3)
            # logger.info("即将开始下载音频...")
            print("即将开始下载音频...")
            download_with_progress(audio_url, headers, f"{bv_path}/audio.mp3")
            # logger.info("音频下载完成")
            print("音频下载完成")
            # logger.info(f"视频 {title_text} 爬取完毕")
            print(f"视频 {title_text} 爬取完毕")

            output_path = f"{file_path}/output"
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            time.sleep(3)
            bitrate = read_properties_from_config("bitrate")
            GPU = read_properties_from_config("gpu_acceleration")
            output_file = f"{title_text}.mp4"
            merge_files(bv_path, output_path, output_file, GPU=GPU, bitrate=bitrate)
            # logger.info("视频与音频已合并")
            print("视频与音频已合并")
        else:
            # logger.error("视频爬取失败")
            print("JSON数据中未找到有效url")
    except Exception as e:
        # logger.error(f"视频爬取失败：{e}")
        print(f"视频爬取失败：{e}")


def get_anime_json(tree, file_path):
    # 提取视频和源音频源信息
    vd_ad_source = tree.xpath('/html/head/script[3]/text()')[0]
    # 去除前面的 const playurlSSRData = 部分，只保留JSON数据
    json_match = re.search(r'const playurlSSRData\s*=\s*({.*})', vd_ad_source)
    if json_match:
        json_data = json_match.group(1)  # 提取花括号内的JSON部分
        json_source = json.loads(json_data)
        json_path = f"{file_path}/json"
        # logger.info(f"保存视频源信息：{json_path}/vd_ad_source.json")
        print(f"保存视频源信息：{json_path}/vd_ad_source.json")
        if not os.path.exists(json_path):
            os.makedirs(json_path)
        with open(f"{json_path}/vd_ad_source.json", "w", encoding="utf-8") as f:
            json.dump(json_source, f, ensure_ascii=False, indent=4)
        # 获取视频和源音频源信息
        video_url = json_source["data"]["result"]["video_info"]["dash"]["video"][0]["base_url"]
        # logger.info(f"video_url:{video_url}")
        audio_url = json_source["data"]["result"]["video_info"]["dash"]["audio"][0]["base_url"]
        # logger.info(f"audio_url:{audio_url}")
        return video_url, audio_url
    else:
        print("未找到有效的JSON数据")
        return None, None


def get_video_json(tree, file_path):
    # 提取视频和源音频源信息
    vd_ad_source = tree.xpath('/html/head/script[4]/text()')[0]
    # 去除前面的 window.__playinfo__= 部分，只保留JSON数据
    json_match = re.search(r'window\.__playinfo__\s*=\s*({.*})', vd_ad_source)
    if json_match:
        json_data = json_match.group(1)  # 提取花括号内的JSON部分
        json_source = json.loads(json_data)
        json_path = f"{file_path}/json"
        # logger.info(f"保存视频源信息：{json_path}/vd_ad_source.json")
        print(f"保存视频源信息：{json_path}/vd_ad_source.json")
        if not os.path.exists(json_path):
            os.makedirs(json_path)
        with open(f"{json_path}/vd_ad_source.json", "w", encoding="utf-8") as f:
            json.dump(json_source, f, ensure_ascii=False, indent=4)
        # 获取视频和源音频源信息
        video_url = json_source["data"]["dash"]["video"][0]["baseUrl"]
        # logger.info(f"video_url:{video_url}")
        audio_url = json_source["data"]["dash"]["audio"][0]["baseUrl"]
        # logger.info(f"audio_url:{audio_url}")
        return video_url, audio_url
    else:
        print("未找到有效的JSON数据")
        return None, None

# if __name__ == "__main__":
#     run_video_crawler()
