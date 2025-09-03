from bilibili import *
def load_proxy_list(proxy_file_path, proxy_filename):
    """
    从CSV文件加载代理列表
    """
    import pandas as pd
    import os
    df = pd.read_csv(str(os.path.join(proxy_file_path, proxy_filename)))
    # df_socks = df[df['PROTOCOL'].str.contains('SOCK', case=False, na=False)]
    proxy_list = []
    for _, row in df[['IP', 'PORT']].iterrows():
        proxy_list.append({
            'http': f"http://{row['IP']}:{row['PORT']}",
            'https': f"http://{row['IP']}:{row['PORT']}"
        })
    return proxy_list

def resource_path(relative_path):
    import sys
    import os
    # 获取资源文件的绝对路径，适用于开发环境和PyInstaller打包环境
    if getattr(sys, 'frozen', False):  # 判断是否是打包后的环境
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 程序配置函数
def get_all_common_config():
    try:
        with open(resource_path('app_config/common_config.txt'), 'r', encoding='utf-8') as f:
            configs = f.readlines()
            return configs
    except FileNotFoundError:
        print('找不到"common_config.txt"文件！\n请确保文件存在且格式正确。')
        pass

def read_properties_from_config(config_name):
    """从文件中读取配置"""
    configs = get_all_common_config()
    for config in configs:
        if config.split(":")[0] == config_name:
            return config.split(":")[1].strip()
    print(f"未找到配置项：{config_name}")
    return 'nan'

def save_properties_to_config(properties_list):
    """将属性保存到配置文件"""
    try:
        with open(resource_path('app_config/common_config.txt'), 'w', encoding='utf-8') as f:
            for property in properties_list:
                f.write(property)
    except Exception as e:
        print(f'保存配置文件时出错：{str(e)}')

def update_properties_in_config(config_name, new_value):
    """更新配置文件中的属性"""
    configs = get_all_common_config()
    for i, config in enumerate(configs):
        if config.split(":")[0] == config_name:
            configs[i] = f"{config_name}: {new_value}\n"
            break
    save_properties_to_config(configs)

def get_cookies_string():
    import json
    try:
        with open(resource_path("./app_config/cookies.json"), "r") as f:
            cookies = json.load(f)
    except FileNotFoundError:
        logger.error('找不到"cookies.json"文件！\n请确保文件存在且格式正确。')
        return None

    cookies_str = ""
    for cookie in cookies:
        cookies_str += cookie["name"] + "=" + cookie["value"] + "; "
    return cookies_str


def get_cookies_expiry_info_formatted():
    import json
    from datetime import datetime
    """
    从cookies.json文件中获取所有cookie的过期时间信息，并以年月日格式显示
    """
    try:
        # 读取cookies.json文件
        cookies_path = resource_path("./app_config/cookies.json")
        with open(cookies_path, 'r', encoding='utf-8') as f:
            cookies_data = json.load(f)

        # 提取所有expiry信息并转换为年月日格式
        expiry_info = []
        for cookie in cookies_data:
            if 'expiry' in cookie:
                # 将Unix时间戳转换为年月日格式
                expiry_timestamp = cookie['expiry']
                expiry_date = datetime.fromtimestamp(expiry_timestamp)
                formatted_date = expiry_date.strftime('%Y年%m月%d日')

                expiry_info.append({
                    'name': cookie['name'],
                    'expiry_timestamp': expiry_timestamp,
                    'expiry_date': formatted_date
                })

        return expiry_info
    except FileNotFoundError:
        print("Cookies文件未找到")
        return []
    except json.JSONDecodeError:
        print("Cookies文件格式错误")
        return []
    except Exception as e:
        print(f"读取cookies过期信息时出错: {e}")
        return []

def display_cookies_expiry_info():
    """
    显示所有cookies的过期时间信息
    """
    expiry_info = get_cookies_expiry_info_formatted()

    if not expiry_info:
        print("没有找到cookies过期信息")
        return

    print("Cookies过期时间信息:")
    print("-" * 50)
    for cookie in expiry_info:
        print(f"Cookie名称: {cookie['name']}")
        print(f"过期时间: {cookie['expiry_date']}")
        print("-" * 30)


# 你也可以在现有的check_cookies_expiry_status函数中添加日期格式显示
def check_cookies_expiry_status_with_dates():
    import json
    from datetime import datetime
    """
    检查cookies的过期状态，并显示详细日期信息
    """
    try:
        cookies_path = resource_path("./app_config/cookies.json")
        with open(cookies_path, 'r', encoding='utf-8') as f:
            cookies_data = json.load(f)

        # 检查是否有即将过期或已过期的cookies
        import time
        current_time = time.time()
        current_date = datetime.fromtimestamp(current_time)
        print(f"当前日期: {current_date.strftime('%Y年%m月%d日')}")
        print("=" * 50)

        expired_cookies = []
        expiring_soon_cookies = []
        valid_cookies = []

        for cookie in cookies_data:
            if 'expiry' in cookie:
                expiry_time = cookie['expiry']
                cookie_name = cookie.get('name', 'Unknown')
                expiry_date = datetime.fromtimestamp(expiry_time)
                formatted_expiry_date = expiry_date.strftime('%Y年%m月%d日')

                cookie_info = {
                    'name': cookie_name,
                    'expiry_date': formatted_expiry_date,
                    'days_until_expiry': (expiry_time - current_time) / (24 * 3600)
                }

                if current_time > expiry_time:
                    expired_cookies.append(cookie_info)
                elif (expiry_time - current_time) < 7 * 24 * 3600:  # 一周内过期
                    expiring_soon_cookies.append(cookie_info)
                else:
                    valid_cookies.append(cookie_info)

        # 显示已过期的cookies
        if expired_cookies:
            print("已过期的Cookies:")
            for cookie in expired_cookies:
                print(f"  - {cookie['name']}: {cookie['expiry_date']} (已过期)")
            print()

        # 显示即将过期的cookies
        if expiring_soon_cookies:
            print("即将过期的Cookies (一周内):")
            for cookie in expiring_soon_cookies:
                print(f"  - {cookie['name']}: {cookie['expiry_date']} "
                      f"(还有{cookie['days_until_expiry']:.1f}天)")
            print()

        # 显示有效的cookies
        if valid_cookies:
            print("有效的Cookies:")
            for cookie in valid_cookies:
                print(f"  - {cookie['name']}: {cookie['expiry_date']} "
                      f"(还有{cookie['days_until_expiry']:.1f}天)")
            print()

        return {
            'expired': expired_cookies,
            'expiring_soon': expiring_soon_cookies,
            'valid': valid_cookies
        }
    except Exception as e:
        print(f"检查cookies过期状态时出错: {e}")
        return {'expired': [], 'expiring_soon': [], 'valid': []}

def get_remain_time(cookie_name):
    import time
    cookies = get_cookies_expiry_info_formatted()
    cookie = [cookie for cookie in cookies if cookie.get("name") == cookie_name][0]
    return int((cookie["expiry_timestamp"] - time.time()) / 86400)


# 带进度条的下载函数
def download_with_progress(url, headers, filename):
    import requests
    from tqdm import tqdm
    response = requests.get(url, headers=headers, stream=True, timeout=10)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1KB块
    # 转换为MB并保留2位小数
    total_size_mb = round(total_size / (1024 * 1024), 2)
    # logger.info(f"下载文件大小：{total_size_mb} MB")
    print(f"下载文件大小：{total_size_mb} MB")
    with open(filename, "wb") as file, tqdm(
            desc=filename,
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
    ) as progress_bar:
        for data in response.iter_content(block_size):
            size = file.write(data)
            progress_bar.update(size)

def merge_files(file_paths, output_path, output_file, GPU, bitrate):
    from moviepy.video.io.VideoFileClip import VideoFileClip, AudioFileClip
    import os
    video = VideoFileClip(f"{file_paths}/video.mp4")
    audio = AudioFileClip(f"{file_paths}/audio.mp3")
    # logger.info("即将开始合并视频和音频...")
    print("即将开始合并视频和音频...")
    bv = video.with_audio(audio)

    # 如果提供了封面图片，则在写入时设置封面
    output_full_path = output_path + "/" + output_file
    if GPU == "nan":
        bv.write_videofile(
            output_full_path,
        )
    elif GPU == "NVIDIA":
        # bv.write_videofile(output_full_path)
        # 使用NVIDIA NVENC进行GPU加速
        bv.write_videofile(
            output_full_path,
            codec="h264_nvenc",  # NVIDIA GPU编码器
            audio_codec="aac",
            bitrate=bitrate,  # 可根据需要调整
            threads=1  # GPU编码时通常不需要多线程
        )
    elif GPU == "AMD":
        bv.write_videofile(
            output_full_path,
            codec="h264_amf",  # AMD GPU编码器
            audio_codec="aac",
            bitrate=bitrate,  # 可根据需要调整
            threads=1  # GPU编码时通常不需要多线程
        )
    elif GPU == "Intel":
        bv.write_videofile(
            output_full_path,
            codec="h264_qsv",  # Intel GPU编码器
            audio_codec="aac",
            bitrate=bitrate,  # 可根据需要调整
            threads=1  # GPU编码时通常不需要多线程
        )
    else:
        print("不支持的GPU类型")

    # 清理资源
    video.close()
    audio.close()
    bv.close()

    # 删除原始视频和音频文件
    # is_delete_origin = input("是否删除原始视频和音频文件？(y/n):")
    # if is_delete_origin == "y":
    #     try:
    #         os.remove(f"{file_paths}/video.mp4")
    #         os.remove(f"{file_paths}/audio.mp3")
    #         logger.info("已删除原始视频和音频文件")
    #     except Exception as e:
    #         logger.error(f"删除原始文件时出错: {e}")
    is_delete_origin = read_properties_from_config("is_delete_origin")
    if is_delete_origin == "true":
        try:
            os.remove(f"{file_paths}/video.mp4")
            os.remove(f"{file_paths}/audio.mp3")
            print("已删除原始视频和音频文件")
        except Exception as e:
            print(f"删除原始文件时出错: {e}")


