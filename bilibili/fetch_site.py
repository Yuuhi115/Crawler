import time

from lxml import html
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.edge.service import Service as EdgeService
from utils import *


class BilibiliLoginCrawler:
    def __init__(self, base_url = "https://www.bilibili.com"):
        self.username = read_properties_from_config("username")
        self.password = read_properties_from_config("password")
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
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0')
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
                username_input = self.driver.find_element(By.XPATH, '//div[@class="login-pwd-wp"]//div[@class="form__item"]/input[@type="text"]')
                password_input = self.driver.find_element(By.XPATH, '//div[@class="login-pwd-wp"]//div[@class="form__item"]/input[@type="password"]')
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
        time.sleep(3)
        crawler.driver.refresh()
        time.sleep(3)
        crawler.quit_crawler()

def run_crawler_login():
    # proxy_list = load_proxy_list(proxy_file_path="../proxy_ip", proxy_filename="proxy_ip_china.csv")
    # print("代理列表：", proxy_list)
    crawler = BilibiliLoginCrawler()
    if crawler.init_browser():
        crawler.login()
        time.sleep(5)
        crawler.quit_crawler()

def run_search_page(key_word):
    # key_word = input("请输入搜索词: ")
    crawler = BilibiliLoginCrawler("https://search.bilibili.com/video?keyword="+key_word)
    if crawler.init_browser():
        crawler.search_page()




# def main():
#     run_crawler_login()
#     run_crawler_fetch_page()

# if __name__ == "__main__":
#     main()