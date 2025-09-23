import os.path
import time
from itertools import batched
import wx

from lxml import html
import json
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.edge.service import Service as EdgeService
from utils import *


class BilibiliLoginCrawler:
    def __init__(self, base_url="https://www.bilibili.com", username=None, password=None):
        self.username = username
        self.password = password
        # self.proxy_list = proxy_list
        self.proxy_list = None
        self.proxy_port = ""
        self.proxy_host = ""
        self.base_url = base_url
        # 初始化WebDriver
        self.driver = None
        self.content = None
        self.tree = None

    def init_browser(self):
        # # 随机选择一个代理
        # proxy_dict = random.choice(self.proxy_list)
        # print(f"使用代理：{proxy_dict}")
        # proxy_url = proxy_dict.get("http")
        # # 解析主机和端口
        # proxy_parts = proxy_url.split('://')[1].split(':')
        # self.proxy_host = proxy_parts[0]
        # self.proxy_port = proxy_parts[1]

        # 创建EdgeOptions对象，配置option
        option = webdriver.EdgeOptions()
        # if self.proxy_host and self.proxy_port:
        #     proxy = f"{self.proxy_host}:{self.proxy_port}"
        #     option.add_argument(f"--proxy-server=http://{proxy}")

        # 设置User-Agent等参数
        option.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0')
        option.add_argument('--disable-blink-features=AutomationControlled')
        option.add_experimental_option("excludeSwitches", ["enable-automation"])
        option.add_experimental_option('useAutomationExtension', False)

        # 隐藏webdriver特征
        option.add_argument("--disable-blink-features")
        option.add_argument("--disable-blink-features=AutomationControlled")

        try:
            # 手动指定 WebDriver 路径
            service = EdgeService(executable_path=resource_path("./msedgedriver.exe"))
            # 创建EdgeDriver对象
            self.driver = webdriver.Edge(service=service, options=option)

            # 设置各种超时
            self.driver.set_page_load_timeout(30)  # 页面加载超时30秒
            self.driver.implicitly_wait(10)  # 隐式等待10秒
            self.driver.set_script_timeout(20)  # 脚本执行超时20秒

            # 执行脚本隐藏webdriver特征
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            # 抹掉selenium中的自动化特征
            with open(resource_path('./stealth.min.js'), 'r') as f:
                js = f.read()
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': js})

            return True
        except Exception as e:
            print(f"初始化浏览器失败：{e}")
            try:
                # 即使WebDriver初始化失败，我们仍然可以尝试获取版本信息
                # 通过命令行方式获取浏览器版本
                import subprocess
                import re

                # 获取Edge浏览器版本
                try:
                    # Windows下获取Edge版本的命令
                    result = subprocess.run(
                        ['reg', 'query', 'HKEY_CURRENT_USER\\Software\\Microsoft\\Edge\\BLBeacon', '/v', 'version'],
                        capture_output=True, text=True, check=True
                    )
                    web_version = re.search(r'version\s+REG_SZ\s+(.*)', result.stdout).group(1).strip()
                    web_version_main = web_version.split('.')[0]
                except:
                    # 备用方法
                    try:
                        result = subprocess.run(
                            ['powershell', 'Get-AppxPackage', 'Microsoft.MicrosoftEdge.Stable'],
                            capture_output=True, text=True, check=True
                        )
                        version_match = re.search(r'Version\s*:\s*([^\s]+)', result.stdout)
                        web_version = version_match.group(1) if version_match else "unknown"
                        web_version_main = web_version.split('.')[0] if web_version != "unknown" else "unknown"
                    except:
                        web_version = "unknown"
                        web_version_main = "unknown"

                # 获取驱动版本
                try:
                    # 使用命令行方式执行驱动程序获取版本
                    import os
                    driver_path = resource_path("./msedgedriver.exe")
                    if os.path.exists(driver_path):
                        result = subprocess.run([driver_path, '--version'], capture_output=True, text=True, check=True)
                        driver_version_output = result.stdout.strip()
                        # 提取版本号
                        driver_version = driver_version_output.split(' ')[3]  # 假设输出格式为 "msedgedriver version 123.456.789.0"
                        driver_version_main = driver_version.split('.')[0]
                    else:
                        driver_version = "unknown"
                        driver_version_main = "unknown"
                except:
                    driver_version = "unknown"
                    driver_version_main = "unknown"

                if web_version_main != driver_version_main and web_version_main != "unknown" and driver_version_main != "unknown":
                    message = (
                        f"当前浏览器版本:{web_version}，浏览器驱动版本:{driver_version}\n请点击'是'下载对应的驱动版本，并将解压后的exe文件移动到{resource_path('msedgedriver.exe')}"
                        f"\nTips:替换驱动版本前，请打开任务管理器，将任务中包含Microsoft Edge WebDriver的进程结束。")
                    result = wx.MessageBox(message, "提示", wx.YES_NO | wx.ICON_INFORMATION)
                    print(message)
                    if result == wx.YES:
                        import webbrowser
                        webbrowser.open(
                            f"https://msedgewebdriverstorage.z22.web.core.windows.net/?prefix={web_version}/")
                        return False
                elif web_version == "unknown":
                    print("无法检测到Edge浏览器版本，请确保已安装Microsoft Edge浏览器")
                elif driver_version == "unknown":
                    print("无法检测到Edge驱动版本，请确保msedgedriver.exe文件存在且可执行")
            except Exception as version_error:
                print(f"检测版本信息时出错: {version_error}")
            return False

    def get_cookies(self):
        # 读取并添加cookie
        with open(resource_path("./app_config/cookies.json"), "r") as f:
            cookies = json.load(f)
        for cookie in cookies:
            self.driver.add_cookie(cookie)

    def fetch_page(self):
        try:
            self.driver.get(self.base_url)
            time.sleep(5)
            self.content = self.driver.page_source
            # print(self.content)
            # 检查最终是否成功获取内容
        except TimeoutException:
            print("页面加载超时")

    def search_page(self):
        try:
            self.driver.get(self.base_url)
        except Exception as e:
            print(f"搜索页面加载失败：{e}")

    def login(self):
        try:
            self.driver.get(self.base_url)
            time.sleep(2)
            self.content = self.driver.page_source
            # print(self.content)
            # 检查最终是否成功获取内容
            if self.content and len(self.content) >= 500:
                self.tree = html.fromstring(self.content)
                login_window_button = self.driver.find_element(By.XPATH, '//div[@class="header-login-entry"]')
                login_window_button.click()
                time.sleep(2)
                username_input = self.driver.find_element(By.XPATH,
                                                          '//div[@class="login-pwd-wp"]//div[@class="form__item"]/input[@type="text"]')
                password_input = self.driver.find_element(By.XPATH,
                                                          '//div[@class="login-pwd-wp"]//div[@class="form__item"]/input[@type="password"]')
                username_input.send_keys(self.username)
                time.sleep(1)
                password_input.send_keys(self.password)
                time.sleep(1)
                login_button = self.driver.find_element(By.XPATH, '//div[@class="btn_wp"]/div[2]')
                login_button.click()
                # logger.info("请手动进行登录验证操作! 稍后浏览器将自动跳转并获取cookie")

                original_message = "请手动进行登录验证操作! 稍后浏览器将自动跳转并获取cookie"
                # print(original_message)

                import sys
                for i in range(60, 0, -1):
                    sys.stdout.write(f"\r{original_message} 倒计时: {i}秒")
                    sys.stdout.flush()
                    time.sleep(1)
                sys.stdout.write(f"\r{original_message} 倒计时: 完成!")
                sys.stdout.flush()
                time.sleep(1)
                sys.stdout.write("\n")
                sys.stdout.flush()
                # input("请在完成登录并回到主界面后按任意键获取cookies...")
                # logger.info("开始获取cookies")

                print("开始获取cookies")
                self.content = self.driver.page_source
                time.sleep(1)
                cookies = self.driver.get_cookies()
                # logger.info("cookie获取成功")
                print("cookie获取成功")
                with open(resource_path("./app_config/cookies.json"), "w") as f:
                    json.dump(cookies, f, indent=4)
                # logger.info("保存cookies至本地成功")
                print("保存cookies至本地成功")
            else:
                print("无法获取有效页面内容")
                return False
        except Exception as e:
            print(f"登录失败：{e}")

    def login_with_QR_code(self):
        try:
            self.driver.get(self.base_url)
            time.sleep(2)
            self.content = self.driver.page_source
            # print(self.content)
            # 检查最终是否成功获取内容
            if self.content and len(self.content) >= 500:
                self.tree = html.fromstring(self.content)
                login_window_button = self.driver.find_element(By.XPATH, '//div[@class="header-login-entry"]')
                time.sleep(1)
                login_window_button.click()

                original_message = "请手动进行扫码登录验证操作! 稍后浏览器将自动跳转并获取cookie"
                # print(original_message)

                import sys
                for i in range(30, 0, -1):
                    sys.stdout.write(f"\r{original_message} 倒计时: {i}秒")
                    sys.stdout.flush()
                    time.sleep(1)
                sys.stdout.write(f"\r{original_message} 倒计时: 完成!")
                sys.stdout.flush()
                time.sleep(1)
                sys.stdout.write("\n")
                sys.stdout.flush()

                print("开始获取cookies")
                self.content = self.driver.page_source
                time.sleep(1)
                cookies = self.driver.get_cookies()
                # logger.info("cookie获取成功")
                print("cookie获取成功")
                with open(resource_path("./app_config/cookies.json"), "w") as f:
                    json.dump(cookies, f, indent=4)
                # logger.info("保存cookies至本地成功")
                print("保存cookies至本地成功")
                return True
            else:
                print("无法获取有效页面内容")
                return False
        except Exception as e:
            print(f"使用二维码登录失败：{e}")
            return False

    def quit_crawler(self):
        if self.driver:
            self.driver.quit()


def run_crawler_fetch_page():
    # proxy_list = load_proxy_list(proxy_file_path="../proxy_ip", proxy_filename="proxy_ip_china.csv")
    # print("代理列表：", proxy_list)
    crawler = BilibiliLoginCrawler()

    if crawler.init_browser():
        crawler.fetch_page()
        crawler.get_cookies()
        time.sleep(1)
        crawler.driver.refresh()
        time.sleep(3)
        crawler.quit_crawler()


def run_crawler_login(username, password):
    # proxy_list = load_proxy_list(proxy_file_path="../proxy_ip", proxy_filename="proxy_ip_china.csv")
    # print("代理列表：", proxy_list)
    crawler = BilibiliLoginCrawler(username=username, password=password)
    if crawler.init_browser():
        login_status = crawler.login_with_QR_code()
        time.sleep(5)
        crawler.quit_crawler()
        return login_status
    return False


def run_search_page(key_word):
    # key_word = input("请输入搜索词: ")
    crawler = BilibiliLoginCrawler("https://search.bilibili.com/video?keyword=" + key_word)
    if crawler.init_browser():
        crawler.search_page()


def run_favorite_category(uid):
    import requests
    cookie = get_cookies_string()
    print(f"正在获取用户{uid}的收藏夹列表...", )
    # url = f"https://space.bilibili.com/{uid}/favlist"
    url = f"https://api.bilibili.com/x/v3/fav/folder/created/list-all?up_mid={uid}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0",
        "Cookie": cookie,
        "Referer": f"https://space.bilibili.com/{uid}/favlist"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        try:
            fav_json_data = json.loads(response.text)
            return fav_json_data.get("data").get("list")
        except json.JSONDecodeError:
            print("收藏夹JSON解析错误")
            print("原始响应内容:")
            print(response.text)
    else:
        print("获取收藏夹列表失败")


def run_uploader_page(uid):
    import pandas as pd
    crawler = BilibiliLoginCrawler()
    if crawler.init_browser():
        crawler.fetch_page()
        crawler.get_cookies()
        time.sleep(1)
        crawler.driver.refresh()
        time.sleep(1)
        base_url = f"https://space.bilibili.com/{uid}/upload/video"
        crawler.driver.get(base_url)
        time.sleep(4)
        for i in range(10):
            crawler.driver.execute_script(f'document.documentElement.scrollTop={(i + 1) * 1000}')
        time.sleep(1)
        page_num_str = ""
        try:
            page_num_str = crawler.driver.find_element(By.XPATH,
                                                       '//div[@class="vui_pagenation-go"]/span[@class="vui_pagenation-go__count"]')
        except:
            pass
        page_number = 1
        if page_num_str != "":
            page_num_str = page_num_str.text
            start = page_num_str.find("共") + 1
            end = page_num_str.find("页")
            page_number = int(page_num_str[start:end].strip())

        video_title_list = []
        video_link_list = []

        crawler.content = crawler.driver.page_source
        crawler.tree = html.fromstring(crawler.content)
        uploader_name = crawler.tree.xpath('//div[@class="nickname"]/text()')[0]

        for page_num in range(1, int(page_number + 1)):
            print(f"正在获取 {uploader_name} 的视频列表 第{page_num}页")

            # 滚动到页面底部
            next_page_text_sizer = None
            try:
                next_page_text_sizer = crawler.driver.find_element(By.XPATH,
                                                                   '//input[@class="vui_input__input vui_input__input-resizable"]')
            except:
                pass
            if next_page_text_sizer is not None:
                if page_num != 1:
                    next_page_text_sizer.send_keys(page_num)
                    time.sleep(1)
                    next_page_text_sizer.send_keys(Keys.ENTER)
                    time.sleep(4)
                for i in range(10):
                    crawler.driver.execute_script(f'document.documentElement.scrollTop={(i + 1) * 1000}')
            time.sleep(1)
            crawler.content = crawler.driver.page_source
            crawler.tree = html.fromstring(crawler.content)
            video_title_list_page = crawler.tree.xpath('//div[@class="bili-video-card__title"]/a/text()')
            video_link_list_page = crawler.tree.xpath('//div[@class="bili-video-card__title"]/a/@href')
            for video_title in video_title_list_page:
                video_title_list.append(video_title)
                print(f"视频标题: {video_title}")
            for video_link in video_link_list_page:
                video_link_list.append(video_link)
        print(f"title_list_size:{len(video_title_list)}")
        print(f"link_list_size:{len(video_link_list)}")
        df = pd.DataFrame({"title": video_title_list, "link": video_link_list, "download_status": 0})
        output_path = "batch_list"
        if not os.path.exists(resource_path(output_path)):
            os.mkdir(resource_path(output_path))
        df.to_excel(resource_path(f"{output_path}/{uploader_name}_upload_video.xlsx"), index=False)
        print(f"{uploader_name}上传视频列表已保存至 {resource_path(f"{output_path}\\{uploader_name}_upload_video.xlsx")}")
        time.sleep(1)
        crawler.quit_crawler()


def run_favorite_category_page(uid, fid, f_title):
    import pandas as pd
    crawler = BilibiliLoginCrawler()
    if crawler.init_browser():
        crawler.fetch_page()
        crawler.get_cookies()
        time.sleep(1)
        crawler.driver.refresh()
        time.sleep(1)
        base_url = f"https://space.bilibili.com/{uid}/favlist?fid={fid}&ftype=create"
        crawler.driver.get(base_url)
        print(f"正在检索用户 {uid} 的收藏夹 {f_title}")
        time.sleep(4)
        # 滚动到页面底部
        for i in range(10):
            crawler.driver.execute_script(f'document.documentElement.scrollTop={(i + 1) * 1000}')
        time.sleep(1)
        page_num_str = ""
        try:
            page_num_str = crawler.driver.find_element(By.XPATH,
                                                       '//div[@class="vui_pagenation-go"]/span[@class="vui_pagenation-go__count"]')
        except:
            pass
        page_number = 1
        if page_num_str != "":
            page_num_str = page_num_str.text
            start = page_num_str.find("共") + 1
            end = page_num_str.find("页")
            page_number = int(page_num_str[start:end].strip())

        video_title_list = []
        video_link_list = []

        crawler.content = crawler.driver.page_source
        crawler.tree = html.fromstring(crawler.content)
        user_name = crawler.tree.xpath('//div[@class="nickname"]/text()')[0]

        for page_num in range(1, int(page_number + 1)):
            print(f"正在获取 {user_name} 的收藏夹 {f_title} 第{page_num}页")

            next_page_text_sizer = None
            try:
                next_page_text_sizer = crawler.driver.find_element(By.XPATH,
                                                                   '//input[@class="vui_input__input vui_input__input-resizable"]')
            except:
                pass
            if next_page_text_sizer is not None:
                if page_num != 1:
                    next_page_text_sizer.send_keys(page_num)
                    time.sleep(1)
                    next_page_text_sizer.send_keys(Keys.ENTER)
                    time.sleep(4)
                for i in range(10):
                    crawler.driver.execute_script(f'document.documentElement.scrollTop={(i + 1) * 1000}')
            time.sleep(1)
            crawler.content = crawler.driver.page_source
            crawler.tree = html.fromstring(crawler.content)
            video_title_list_page = crawler.tree.xpath('//div[@class="items"]/div[@class="items__item"]//div[@class="bili-video-card__title bili-video-card__title--pr"]/a/text()')
            video_link_list_page = crawler.tree.xpath('//div[@class="items"]/div[@class="items__item"]//div[@class="bili-video-card__title bili-video-card__title--pr"]/a/@href')
            for video_title in video_title_list_page:
                video_title_list.append(video_title)
                print(f"视频标题: {video_title}")
            for video_link in video_link_list_page:
                video_link_list.append(video_link)
        print(f"title_list_size:{len(video_title_list)}")
        print(f"link_list_size:{len(video_link_list)}")
        df = pd.DataFrame({"title": video_title_list, "link": video_link_list, "download_status": 0})
        df = df[df['title'] != '已失效视频']

        output_path = "batch_list"
        if not os.path.exists(resource_path(output_path)):
            os.mkdir(resource_path(output_path))
        time.sleep(1)
        df.to_excel(resource_path(f"{output_path}/{user_name}_favorite_{f_title}.xlsx"), index=False)
        print(f"收藏夹 {f_title} 视频列表已保存至 {resource_path(f"{output_path}\\{user_name}_favorite_{f_title}.xlsx")}")
        time.sleep(1)
        crawler.quit_crawler()

# def main():
#     run_crawler_login()
#     run_crawler_fetch_page()

# if __name__ == "__main__":
#     main()
