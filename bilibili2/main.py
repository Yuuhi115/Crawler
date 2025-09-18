from fetch_site import *
from fetch_video import *


def attempt_login():
    account = input("请输入账号: ")
    password = input("请输入密码: ")
    is_check = input("请务必确认账号与密码都正确，否则无法获取cookies (y/n): ")
    if is_check == "y":
        update_properties_in_config("username", account)
        update_properties_in_config("password", password)
    else:
        print("请重新输入")
        time.sleep(1)
    return is_check
def main():
    global url
    logger.info("Program Starting...")
    time.sleep(2)
    while True:
        is_login = input("登录后可下载高清视频，是否登录？(y/n): ")
        if is_login == "y" or is_login == "Y":
            if os.path.exists(resource_path("./app_config/cookies.json")):
                logger.info("已检测到cookies.json文件，将使用cookies登录")
                time.sleep(1)
                is_update = input("长时间未更新cookies将导致登录失效，是否更新cookies？(y/n): ")
                if is_update == "y":
                    if attempt_login() == "y":
                        logger.info("即将进行登录操作...")
                        time.sleep(1)
                        run_crawler_login()
                        break
                else:
                    logger.info("已取消更新cookies")
                    time.sleep(1)
                    break
            else:
                if attempt_login() == "y":
                    logger.info("即将进行登录操作...")
                    time.sleep(1)
                    run_crawler_login()
                    break
                else:
                    logger.info("已取消登录")
                    time.sleep(1)
                    break
        else:
            break
    if input("是否要搜索视频？(y/n): ") == "y":
        key_word = input("请输入搜索词: ")
        run_search_page(key_word)
    url = input("请输入视频链接: ")
    if url != "":
        run_video_crawler(url)
if __name__ == '__main__':
    main()
    while True:
        time.sleep(1)
        try:
            is_continue = input("是否还要继续下载视频? (y/n):")
            if is_continue == "y":
                if input("是否要搜索视频？(y/n): ") == "y":
                    key_word = input("请输入搜索词: ")
                    run_search_page(key_word)
                url = input("请输入视频链接: ")
                if url != "":
                    run_video_crawler(url)
            else:
                break
        except Exception as e:
            logger.error(e)
            logger.error("程序异常，请检查日志")
            time.sleep(5)

