import wx
import threading
import os
from fetch_site import *
from proxy_config_dialog import ProxyConfigDialog
from fetch_video import run_video_crawler
from utils import *
import sys


class BilibiliCrawlerFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="Bilibili视频下载器", size=(600, 600))
        self.panel = wx.Panel(self)
        self.batch_download_stop_flag = False  # 添加终止标志位
        self.batch_download_status = False
        self.cookie_expiry = None
        self.create_ui()
        self.SetMinSize((600, 600))
        self.Center()
        self.SetDoubleBuffered(True)  # 减少界面闪烁

    def get_cookie_expiry(self, cookie_name):
        """
        获取指定cookie的剩余时间
        """
        try:
            return get_remain_time(cookie_name)
        except Exception as e:
            print(f"获取cookie过期时间时出错: {e}")
            self.cookie_expiry = None

    def create_ui(self):
        # 主布局
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # 登录区域
        login_box = wx.StaticBox(self.panel, label="登录设置")
        login_sizer = wx.StaticBoxSizer(login_box, wx.VERTICAL)

        # 账号密码输入
        # account_sizer = wx.FlexGridSizer(2, 2, 5, 5)
        # account_sizer.AddGrowableCol(1)
        #
        # account_sizer.Add(wx.StaticText(self.panel, label="账号:"), 0, wx.ALIGN_CENTER_VERTICAL)
        # self.account_text = wx.TextCtrl(self.panel)
        # account_sizer.Add(self.account_text, 1, wx.EXPAND)
        #
        # account_sizer.Add(wx.StaticText(self.panel, label="密码:"), 0, wx.ALIGN_CENTER_VERTICAL)
        # self.password_text = wx.TextCtrl(self.panel, style=wx.TE_PASSWORD)
        # account_sizer.Add(self.password_text, 1, wx.EXPAND)
        #
        # login_sizer.Add(account_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # 登录按钮
        self.login_btn = wx.Button(self.panel, label="扫码登录并保存Cookies")
        self.login_btn.Bind(wx.EVT_BUTTON, self.on_login)
        login_sizer.Add(self.login_btn, 0, wx.EXPAND | wx.ALL, 5)

        # 检测cookies状态
        self.cookies_status = wx.StaticText(self.panel, label="Cookies状态: 未检测到")
        login_sizer.Add(self.cookies_status, 0, wx.ALL, 5)

        main_sizer.Add(login_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # 其他功能区域
        search_box = wx.StaticBox(self.panel, label="其他功能")
        search_sizer = wx.StaticBoxSizer(search_box, wx.VERTICAL)

        config_box = wx.StaticBox(self.panel, label="配置区域")
        config_sizer = wx.StaticBoxSizer(config_box, wx.VERTICAL)

        search_other_H_sizer_config = wx.BoxSizer(wx.HORIZONTAL)
        search_other_H_sizer_util = wx.BoxSizer(wx.HORIZONTAL)
        self.search_btn = wx.Button(self.panel, label="搜索视频")
        self.search_btn.Bind(wx.EVT_BUTTON, self.on_search)

        self.export_config_btn = wx.Button(self.panel, label="导出设置")
        self.export_config_btn.Bind(wx.EVT_BUTTON, self.on_config)

        self.proxy_config_btn = wx.Button(self.panel, label="代理设置")
        self.proxy_config_btn.Bind(wx.EVT_BUTTON, self.on_proxy_config)

        self.uploader_btn = wx.Button(self.panel, label="获取up主页面")
        self.uploader_btn.Bind(wx.EVT_BUTTON, self.on_open_uploader)

        self.favorite_btn = wx.Button(self.panel, label="检索收藏夹")
        self.favorite_btn.Bind(wx.EVT_BUTTON, self.on_open_favorite)

        self.rotate_video_btn = wx.Button(self.panel, label="视频翻转")
        self.rotate_video_btn.Bind(wx.EVT_BUTTON, self.on_rotate_video)

        self.check_update_btn = wx.Button(self.panel, label="检查更新")
        self.check_update_btn.Bind(wx.EVT_BUTTON, self.on_check_update)

        search_other_H_sizer_util.Add(self.search_btn, 0, wx.ALL, 5)
        search_other_H_sizer_util.Add(self.uploader_btn, 0, wx.ALL, 5)
        search_other_H_sizer_util.Add(self.favorite_btn, 0, wx.ALL, 5)
        search_other_H_sizer_util.Add(self.rotate_video_btn, 0, wx.ALL, 5)
        search_other_H_sizer_util.Add(self.check_update_btn, 0, wx.ALL, 5)

        search_other_H_sizer_config.Add(self.export_config_btn, 0, wx.ALL, 5)
        search_other_H_sizer_config.Add(self.proxy_config_btn, 0, wx.ALL, 5)

        search_sizer.Add(search_other_H_sizer_util, 0, wx.EXPAND)
        config_sizer.Add(search_other_H_sizer_config, 0, wx.EXPAND)

        main_sizer.Add(search_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(config_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # 视频链接区域
        video_box = wx.StaticBox(self.panel, label="视频下载")
        video_sizer = wx.StaticBoxSizer(video_box, wx.VERTICAL)

        url_sizer = wx.BoxSizer(wx.HORIZONTAL)
        url_sizer.Add(wx.StaticText(self.panel, label="视频链接:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.url_text = wx.TextCtrl(self.panel)
        url_sizer.Add(self.url_text, 1, wx.EXPAND | wx.ALL, 5)
        self.download_btn = wx.Button(self.panel, label="下载")
        self.download_btn.Bind(wx.EVT_BUTTON, self.on_download)
        url_sizer.Add(self.download_btn, 0, wx.ALL, 5)

        batch_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.import_batch_btn = wx.Button(self.panel, label="导入视频列表")
        self.import_batch_btn.Bind(wx.EVT_BUTTON, self.on_import_batch)
        batch_sizer.Add(self.import_batch_btn, 0, wx.ALL, 5)

        self.imported_file_label = wx.StaticText(self.panel, label="未选择文件")
        batch_sizer.Add(self.imported_file_label, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.batch_download_btn = wx.Button(self.panel, label="批量下载")
        self.batch_download_btn.Bind(wx.EVT_BUTTON, self.on_batch_download)
        self.batch_download_btn.Enable(False)  # 初始禁用，导入文件后启用
        batch_sizer.Add(self.batch_download_btn, 0, wx.ALL, 5)

        video_sizer.Add(url_sizer, 0, wx.EXPAND)
        video_sizer.Add(batch_sizer, 0, wx.EXPAND)
        main_sizer.Add(video_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # 日志显示区域
        log_box = wx.StaticBox(self.panel, label="运行日志")
        log_sizer = wx.StaticBoxSizer(log_box, wx.VERTICAL)

        self.log_text = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.HSCROLL)
        font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.log_text.SetFont(font)
        log_sizer.Add(self.log_text, 1, wx.EXPAND | wx.ALL, 5)

        # 重定向标准输出到文本框
        sys.stdout = LogTarget(self.log_text)
        sys.stderr = LogTarget(self.log_text, isError=True)

        main_sizer.Add(log_sizer, 1, wx.EXPAND | wx.ALL, 5)

        # 底部按钮
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.clear_btn = wx.Button(self.panel, label="终止批量下载")
        self.clear_btn.Bind(wx.EVT_BUTTON, self.on_stop_batch)
        button_sizer.Add(self.clear_btn, 0, wx.ALL, 5)

        self.clear_btn = wx.Button(self.panel, label="清空日志")
        self.clear_btn.Bind(wx.EVT_BUTTON, self.on_clear_log)
        button_sizer.Add(self.clear_btn, 0, wx.ALL, 5)

        self.exit_btn = wx.Button(self.panel, label="退出")
        self.exit_btn.Bind(wx.EVT_BUTTON, self.on_exit)
        button_sizer.Add(self.exit_btn, 0, wx.ALL, 5)

        main_sizer.Add(button_sizer, 0, wx.ALIGN_RIGHT)

        self.panel.SetSizer(main_sizer)

        # 检查cookies状态
        self.check_cookies_status()

    def check_cookies_status(self):
        """
        检查cookies状态并更新UI显示
        """
        try:
            if os.path.exists(resource_path("./app_config/cookies.json")):
                self.cookie_expiry = self.get_cookie_expiry("SESSDATA")
                if self.cookie_expiry is not None:
                    if self.cookie_expiry > 0:
                        self.cookies_status.SetLabel(
                            f"Cookies状态: 已检测到 (可下载高清视频), 有效期还剩: {self.cookie_expiry} 天")
                    else:
                        self.cookies_status.SetLabel("Cookies状态: 已过期 (需重新登录获取)")
                else:
                    # 如果无法获取过期时间，显示基本状态
                    self.cookies_status.SetLabel("Cookies状态: 已检测到 (可下载高清视频)")
            else:
                self.cookies_status.SetLabel("Cookies状态: 未检测到 (只能下载低清视频)")
        except Exception as e:
            print(f"Error checking cookies status: {e}")
            # 出错时显示默认信息
            self.cookies_status.SetLabel("Cookies状态: 检查出错")

    def on_login(self, event):
        # account = self.account_text.GetValue()
        # password = self.password_text.GetValue()
        #
        # if not account or not password:
        #     wx.MessageBox("请填写账号和密码", "提示", wx.OK | wx.ICON_WARNING)
        #     return

        # 在后台线程中执行登录操作
        # login_thread = threading.Thread(target=self.login_worker, args=(account, password))
        login_thread = threading.Thread(target=self.login_worker)
        login_thread.daemon = True
        login_thread.start()

        self.check_cookies_status()

    def login_worker(self, account = None, password = None):
        # 执行登录
        try:
            if run_crawler_login(username = account, password = password):
                wx.CallAfter(self.on_login_complete)
            else:
                wx.MessageBox("登录失败", "提示", wx.OK | wx.ICON_WARNING)
        except Exception as e:
            wx.MessageBox(f"登录过程中出现错误: {str(e)}", "错误", wx.OK | wx.ICON_ERROR)

    def on_login_complete(self):
        self.check_cookies_status()
        wx.MessageBox("登录成功，Cookies已保存", "提示", wx.OK | wx.ICON_INFORMATION)

    def on_search(self, event):
        # 弹出对话框获取搜索关键词
        dialog = wx.TextEntryDialog(self, "请输入搜索关键词:", "视频搜索", "")
        if dialog.ShowModal() == wx.ID_OK:
            keyword = dialog.GetValue()
            if keyword:
                # 在后台线程中执行搜索操作
                search_thread = threading.Thread(target=self.search_worker, args=(keyword,))
                search_thread.daemon = True
                search_thread.start()
            else:
                wx.MessageBox("请输入搜索关键词", "提示", wx.OK | wx.ICON_WARNING)
        dialog.Destroy()

    def on_config(self, event):
        # 创建配置对话框
        dialog = ExportConfigDialog(self)
        dialog.ShowModal()
        dialog.Destroy()

    def on_proxy_config(self, event):
        """代理设置按钮事件处理"""
        dialog = ProxyConfigDialog(self)
        dialog.ShowModal()
        dialog.Destroy()

    def on_open_uploader(self, event):
        """打开上传页面按钮事件处理"""
        dialog = wx.TextEntryDialog(self, "请输入up主id:", "uid:", "")
        if dialog.ShowModal() == wx.ID_OK:
            uid = dialog.GetValue()
            if uid:
                # 在后台线程中执行搜索操作
                search_space_thread = threading.Thread(target=self.search_space_worker, args=(uid,))
                search_space_thread.daemon = True
                search_space_thread.start()
            else:
                wx.MessageBox("请输入输入up主id", "提示", wx.OK | wx.ICON_WARNING)
        dialog.Destroy()

    def search_space_worker(self, uid):
        try:
            run_uploader_page(uid)
        except Exception as e:
            wx.MessageBox(f"搜索过程中出现错误: {str(e)}", "错误", wx.OK | wx.ICON_ERROR)

    def on_open_favorite(self, event):
        """打开收藏夹页面按钮事件处理"""
        if os.path.exists(resource_path("./app_config/cookies.json")):
            uid = get_cookie_by_name("DedeUserID").get("value")
            fav_category_list = self.search_favorite_category(uid)
            if fav_category_list is not None:
                # 创建收藏夹选项列表
                choices = [f"{fav['title']}" for fav in fav_category_list]
                # 创建单选对话框
                dialog = wx.SingleChoiceDialog(self, "请选择收藏夹:", "收藏夹选择", choices)
                if dialog.ShowModal() == wx.ID_OK:
                    selection = dialog.GetSelection()
                    selected_favorite = fav_category_list[selection]
                    print(f"已选择收藏夹: {selected_favorite['title']} (ID: {selected_favorite['id']})")
                    # 在后台线程中执行搜索操作
                    search_favorite_thread = threading.Thread(target=self.search_favorite_worker, args=(selected_favorite, uid))
                    search_favorite_thread.daemon = True
                    search_favorite_thread.start()
                else:
                    print("未选择收藏夹")
            else:
                wx.MessageBox("系统异常，未获取收藏夹列表", "提示", wx.OK | wx.ICON_WARNING)
        else:
            wx.MessageBox("请先登录！", "提示", wx.OK | wx.ICON_WARNING)

    def search_favorite_category(self, uid):
        try:
            fav_category_list = run_favorite_category(uid)
            if fav_category_list is not None:
                return fav_category_list
        except Exception as e:
            wx.MessageBox(f"搜索收藏夹列表过程中出现错误: {str(e)}", "错误", wx.OK | wx.ICON_ERROR)

    def search_favorite_worker(self, selected_favorite, uid):
        try:
            run_favorite_category_page(uid, selected_favorite['id'], selected_favorite['title'])
        except Exception as e:
            wx.MessageBox(f"检索收藏夹'{selected_favorite['title']}'信息过程中出现错误: {str(e)}", "错误", wx.OK | wx.ICON_ERROR)


    def search_worker(self, key_word):
        try:
            run_search_page(key_word)
        except Exception as e:
            wx.MessageBox(f"搜索过程中出现错误: {str(e)}", "错误", wx.OK | wx.ICON_ERROR)

    def on_download(self, event):
        url = self.url_text.GetValue()
        if not url:
            wx.MessageBox("请输入视频链接", "提示", wx.OK | wx.ICON_WARNING)
            return

        # 检查URL是否包含bilibili视频链接特征
        if not ("www.bilibili.com/video/BV" in url or "www.bilibili.com/bangumi/play/ep" in url):
            wx.MessageBox("请输入有效的Bilibili视频链接", "提示",
                            wx.OK | wx.ICON_WARNING)
            return

        download_thread = threading.Thread(target=self.download_worker, args=(url,))
        download_thread.daemon = True
        download_thread.start()

    def download_worker(self, url):
        try:
            if "www.bilibili.com/video/BV" in url:
                run_video_crawler(url, "video")
            elif "www.bilibili.com/bangumi/play/ep" in url:
                run_video_crawler(url, "anime")
            wx.MessageBox("视频下载完成", "提示", wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            wx.MessageBox(f"下载过程中出现错误: {str(e)}", "错误", wx.OK | wx.ICON_ERROR)

    def on_import_batch(self, event):
        """
        导入视频列表按钮事件处理
        """
        # 创建文件选择对话框
        wildcard = "Excel文件 (*.xlsx)|*.xlsx|CSV文件 (*.csv)|*.csv|所有文件 (*.*)|*.*"
        dialog = wx.FileDialog(self, "选择视频列表文件", wildcard=wildcard,
                               style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if dialog.ShowModal() == wx.ID_OK:
            file_path = dialog.GetPath()
            self.import_batch_worker(file_path)
        dialog.Destroy()

    def import_batch_worker(self, file_path):
        import pandas as pd
        """
        导入视频列表工作线程
        """
        try:
            # 根据文件扩展名读取文件
            if file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
                select_df = df[df['download_status'] == 0]
                exclude_df = df[df['download_status'] == 1]
            elif file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
                select_df = df[df['download_status'] == 0]
                exclude_df = df[df['download_status'] == 1]
            else:
                wx.MessageBox("不支持的文件格式，请选择.xlsx或.csv文件", "错误", wx.OK | wx.ICON_ERROR)
                return

            # 检查必要的列是否存在
            if 'link' not in df.columns:
                wx.MessageBox("文件中缺少'link'列，请确保文件包含视频链接", "错误", wx.OK | wx.ICON_ERROR)
                return

            # 检查title列是否存在
            has_title = 'title' in df.columns
            has_download_status = 'download_status' in df.columns

            # 获取链接列
            links = df['link'].tolist()  # 转换为列表
            select_links = select_df['link'].tolist()

            if not links:
                wx.MessageBox("文件中没有找到有效的视频链接", "提示", wx.OK | wx.ICON_WARNING)
                return

            # 保存批量数据
            self.batch_data = select_df
            self.batch_file_path = file_path

            # 更新UI显示
            file_name = os.path.basename(file_path)
            self.imported_file_label.SetLabel(f"已导入: {file_name} ({len(links)}个视频)")
            self.batch_download_btn.Enable(True)

            # 在日志区域输出即将下载的视频标题名
            print(f"成功导入视频列表文件: {file_path}")
            print(f"共找到 {len(links)} 个视频, 有 {len(exclude_df)} 个视频已下载")

            # 1 替换为 "已下载"，0 替换为 "未下载"
            download_status_list = ['已下载' if status == 1 else '未下载' for status in df['download_status'].tolist()]

            if has_title and has_download_status:
                titles = df['title'].tolist()
                for i, (title, link, download_status) in enumerate(zip(titles, links, download_status_list)):
                    print(f"  {i + 1}. {title}. {download_status}")
            else:
                for i, (link, download_status) in enumerate(zip(links, download_status_list)):
                    print(f"  {i + 1}. {link}. {download_status}")

            wx.MessageBox(f"成功导入 {len(select_links)} 个视频链接, 已下载 {len(exclude_df)} 个", "提示", wx.OK | wx.ICON_INFORMATION)

        except Exception as e:
            error_msg = f"导入视频列表过程中出现错误: {str(e)}"
            print(error_msg)
            wx.MessageBox(error_msg, "错误", wx.OK | wx.ICON_ERROR)

    def on_batch_download(self, event):
        """
        批量下载按钮事件处理
        """
        if self.batch_data is None:
            wx.MessageBox("请先导入视频列表文件", "提示", wx.OK | wx.ICON_WARNING)
            return

        # 在后台线程中执行批量下载操作
        batch_download_thread = threading.Thread(target=self.batch_download_worker_with_progress)
        batch_download_thread.daemon = True
        batch_download_thread.start()

    def batch_download_worker_with_progress(self):
        """
        带进度显示的批量下载工作线程
        """
        try:
            import pandas as pd
            if self.batch_data is None:
                return

            # 读取原始文件以更新状态
            if self.batch_file_path.endswith('.xlsx'):
                original_df = pd.read_excel(self.batch_file_path)
            else:
                original_df = pd.read_csv(self.batch_file_path)
            df = self.batch_data.copy()

            # 重置终止标志
            self.batch_download_stop_flag = False
            self.batch_download_status = True

            # 获取链接列
            links = df['link'].dropna().tolist()  # 删除空值并转换为列表

            if not links:
                wx.MessageBox("文件中没有找到有效的视频链接", "提示", wx.OK | wx.ICON_WARNING)
                return

            print(f"开始批量下载 {len(links)} 个视频...")

            # 逐个下载视频
            success_count = 0
            fail_count = 0

            for i, link in enumerate(links):
                # 检查是否需要终止
                if self.batch_download_stop_flag:
                    print("收到终止请求，停止批量下载...")
                    wx.CallAfter(wx.MessageBox,
                                 f"批量下载已终止!\n已完成: {i} 个\n成功: {success_count} 个\n失败: {fail_count} 个",
                                 "提示", wx.OK | wx.ICON_WARNING)
                    print(f"批量下载已终止! 已完成: {i} 个, 成功: {success_count} 个, 失败: {fail_count} 个")
                    # 保存更新后的状态到原始文件
                    if self.batch_file_path.endswith('.xlsx'):
                        original_df.to_excel(self.batch_file_path, index=False)
                    else:
                        original_df.to_csv(self.batch_file_path, index=False)

                    return
                try:
                    print(f"正在下载第 {i + 1}/{len(links)} 个视频: {link}")

                    # 如果有title列，显示视频标题
                    if 'title' in df.columns and i < len(df['title'].dropna().tolist()):
                        title = df['title'].dropna().tolist()[i]
                        print(f"  视频标题: {title}")

                    # 更新进度信息
                    print(f"进度: {i + 1}/{len(links)} ({((i + 1) / len(links) * 100):.1f}%)")

                    # 根据链接类型调用相应的下载函数
                    if "www.bilibili.com/video/BV" in link:
                        run_video_crawler(link, "video")
                        success_count += 1
                        # 更新原始DataFrame中的download_status
                        # 找到原始DataFrame中对应链接的行索引并更新状态
                        original_index = original_df[original_df['link'] == link].index
                        if not original_index.empty:
                            original_df.loc[original_index[0], 'download_status'] = 1
                    elif "www.bilibili.com/bangumi/play/ep" in link:
                        run_video_crawler(link, "anime")
                        success_count += 1
                        # 更新原始DataFrame中的download_status
                        original_index = original_df[original_df['link'] == link].index
                        if not original_index.empty:
                            original_df.loc[original_index[0], 'download_status'] = 1
                    else:
                        print(f"无效的Bilibili视频链接: {link}")
                        fail_count += 1

                except Exception as e:
                    print(f"下载链接 {link} 时出现错误: {str(e)}")
                    fail_count += 1

                # 添加短暂延迟避免请求过于频繁
                time.sleep(2)

            # 重置终止标志
            self.batch_download_stop_flag = False
            self.batch_download_status = False

            # 显示下载结果
            wx.CallAfter(wx.MessageBox,
                         f"批量下载完成!\n成功: {success_count} 个\n失败: {fail_count} 个",
                         "提示", wx.OK | wx.ICON_INFORMATION)

            print(f"批量下载完成! 成功: {success_count} 个, 失败: {fail_count} 个")
            # df.to_excel(self.batch_file_path, index=False)

        except Exception as e:
            # 重置终止标志
            self.batch_download_stop_flag = False
            error_msg = f"批量下载过程中出现错误: {str(e)}"
            print(error_msg)
            wx.MessageBox(error_msg, "错误", wx.OK | wx.ICON_ERROR)

    def on_rotate_video(self, event):
        """处理视频旋转功能"""
        # 创建文件选择对话框
        wildcard = "视频文件 (*.mp4)|*.mp4|所有文件 (*.*)|*.*"
        dialog = wx.FileDialog(self, "选择要旋转的视频文件",
                               wildcard=wildcard,
                               style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if dialog.ShowModal() == wx.ID_OK:
            input_path = dialog.GetPath()

            # 选择旋转角度
            choices = ["90%", "180%", "270%"]
            angle_dialog = wx.SingleChoiceDialog(self, "请选择旋转角度(顺时针):", "旋转设置", choices)

            if angle_dialog.ShowModal() == wx.ID_OK:
                selection = angle_dialog.GetSelection()
                angles = [90, 180, 270]
                angle = angles[selection]

                # 选择输出文件路径
                save_dialog = wx.FileDialog(self, "保存旋转后的视频",
                                            wildcard="MP4 files (*.mp4)|*.mp4",
                                            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

                if save_dialog.ShowModal() == wx.ID_OK:
                    output_path = save_dialog.GetPath()

                    # 确保输出路径以.mp4结尾
                    if not output_path.endswith('.mp4'):
                        output_path += '.mp4'

                    # 在后台线程中执行旋转操作
                    rotate_thread = threading.Thread(
                        target=self.rotate_video_worker,
                        args=(input_path, output_path, angle)
                    )
                    rotate_thread.daemon = True
                    rotate_thread.start()

                save_dialog.Destroy()
            angle_dialog.Destroy()

        dialog.Destroy()

    def rotate_video_worker(self, input_path, output_path, angle):
        """视频旋转工作线程"""
        try:
            print(f"开始旋转视频: {input_path}")
            print(f"旋转角度: {angle}度")

            # 执行视频旋转
            success = rotate_video(input_path, output_path, angle)

            if success:
                wx.CallAfter(wx.MessageBox,
                             f"视频旋转完成!\n已保存至: {output_path}",
                             "提示", wx.OK | wx.ICON_INFORMATION)
                print(f"视频旋转完成! 已保存至: {output_path}")
            else:
                wx.CallAfter(wx.MessageBox,
                             "视频旋转失败，请查看日志",
                             "错误", wx.OK | wx.ICON_ERROR)
        except Exception as e:
            error_msg = f"视频旋转过程中出现错误: {str(e)}"
            print(error_msg)
            wx.CallAfter(wx.MessageBox, error_msg, "错误", wx.OK | wx.ICON_ERROR)

    def on_check_update(self, event):
        """
        检查更新按钮事件处理
        """
        check_update_thread = threading.Thread(target=self.check_update_worker)
        check_update_thread.daemon = True
        check_update_thread.start()

    def check_update_worker(self):
        return_dict = check_github_update()
        if return_dict["code"] == 200:
            update_status = return_dict['update_status']
            if update_status == "True":
                # 使用信息对话框显示消息，并在后续提供打开链接的选项
                update_content = return_dict['update_content']
                update_msg = f"{return_dict['update_message']}\n\n更新内容: \n{update_content}\n\n点击'是'打开下载页面"
                update_url = return_dict["update_url"]
                # 在主线程中显示对话框
                wx.CallAfter(self.show_update_dialog, update_msg, update_url, update_content)
            else:
                wx.MessageBox(return_dict['update_message'], "提示", wx.OK | wx.ICON_INFORMATION)
        elif return_dict["code"] == 403:
            wx.MessageBox("请开启代理后再检测更新", "提示", wx.OK | wx.ICON_INFORMATION)
        else:
            wx.MessageBox("未知异常，请联系作者", "错误", wx.OK | wx.ICON_ERROR)

    def show_update_dialog(self, message, url, content):
        """在主线程中显示更新对话框"""
        result = wx.MessageBox(message, "更新提示", wx.YES_NO | wx.ICON_INFORMATION)
        if result == wx.YES:
            import webbrowser
            webbrowser.open(url)

    def on_stop_batch(self, event):
        """
        终止批量下载按钮事件处理
        """
        if hasattr(self, 'batch_download_stop_flag') and self.batch_download_stop_flag == False and self.batch_download_status == True:
            self.batch_download_stop_flag = True
            self.batch_download_status = False
            print("正在发送终止批量下载请求...")
            wx.MessageBox("已发送终止请求，正在停止批量下载...", "提示", wx.OK | wx.ICON_INFORMATION)
        else:
            print("当前没有正在进行的批量下载任务")
            wx.MessageBox("当前没有正在进行的批量下载任务", "提示", wx.OK | wx.ICON_INFORMATION)


    def on_clear_log(self, event):
        self.log_text.Clear()

    def on_exit(self, event):
        self.Close()


class LogTarget:
    def __init__(self, text_ctrl, isError=False):
        self.text_ctrl = text_ctrl
        self.isError = isError

    def write(self, text):
        wx.CallAfter(self.text_ctrl.WriteText, text)

    def flush(self):
        pass


class ExportConfigDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="导出设置", size=(400, 430))
        self.parent = parent
        self.setup_ui()
        self.load_config()
        self.Center()

    def setup_ui(self):
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # 视频导出目录设置
        dir_box = wx.StaticBox(panel, label="视频导出目录")
        dir_sizer = wx.StaticBoxSizer(dir_box, wx.VERTICAL)

        dir_input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.dir_text = wx.TextCtrl(panel)
        dir_input_sizer.Add(self.dir_text, 1, wx.EXPAND | wx.ALL, 5)

        self.dir_btn = wx.Button(panel, label="选择目录...")
        self.dir_btn.Bind(wx.EVT_BUTTON, self.on_browse_dir)
        dir_input_sizer.Add(self.dir_btn, 0, wx.ALL, 5)

        dir_sizer.Add(dir_input_sizer, 0, wx.EXPAND)
        main_sizer.Add(dir_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # 视频码率设置
        bitrate_box = wx.StaticBox(panel, label="视频码率设置")
        bitrate_sizer = wx.StaticBoxSizer(bitrate_box, wx.VERTICAL)

        bitrate_choices = ["1000k", "2000k", "3000k", "4000k", "5000k", "6000k", "7000k", "8000k"]
        self.bitrate_combo = wx.ComboBox(panel, choices=bitrate_choices,
                                         style=wx.CB_DROPDOWN | wx.CB_READONLY)
        bitrate_sizer.Add(self.bitrate_combo, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(bitrate_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # GPU加速选择
        gpu_box = wx.StaticBox(panel, label="GPU加速设置")
        gpu_sizer = wx.StaticBoxSizer(gpu_box, wx.VERTICAL)

        gpu_choices = ["不使用GPU", "NVIDIA", "AMD", "Intel"]
        self.gpu_combo = wx.ComboBox(panel, choices=gpu_choices,
                                     style=wx.CB_DROPDOWN | wx.CB_READONLY)
        gpu_sizer.Add(self.gpu_combo, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(gpu_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # 是否删除原视频
        delete_box = wx.StaticBox(panel, label="删除原视频设置")
        delete_sizer = wx.StaticBoxSizer(delete_box, wx.VERTICAL)

        delete_choices = ["删除原视频与音频", "保留原视频与音频"]
        self.delete_combo = wx.ComboBox(panel, choices=delete_choices,
                                        style=wx.CB_DROPDOWN | wx.CB_READONLY)
        delete_sizer.Add(self.delete_combo, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(delete_sizer, 0, wx.EXPAND | wx.ALL, 5)

        export_format_box = wx.StaticBox(panel, label="导出格式设置")
        export_format_sizer = wx.StaticBoxSizer(export_format_box, wx.VERTICAL)
        self.export_format_combo = wx.ComboBox(panel, choices=["mp4", "mp3"],
                                        style=wx.CB_DROPDOWN | wx.CB_READONLY)
        export_format_sizer.Add(self.export_format_combo, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(export_format_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # 按钮区域
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ok_btn = wx.Button(panel, wx.ID_OK, label="确定")
        self.ok_btn.Bind(wx.EVT_BUTTON, self.on_ok)
        button_sizer.Add(self.ok_btn, 0, wx.ALL, 5)

        self.cancel_btn = wx.Button(panel, wx.ID_CANCEL, label="取消")
        button_sizer.Add(self.cancel_btn, 0, wx.ALL, 5)

        main_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER)

        panel.SetSizer(main_sizer)

    def load_config(self):
        # 从配置文件加载设置
        export_dir = read_properties_from_config("export_dir")
        if '@-@' in export_dir:
            export_dir = export_dir.replace('@-@', ':')
        bitrate = read_properties_from_config("bitrate")
        gpu_setting = read_properties_from_config("gpu_acceleration")
        delete_setting = read_properties_from_config("is_delete_origin")
        export_format = read_properties_from_config("export_format")

        # 设置默认值
        if export_dir != "":
            self.dir_text.SetValue(export_dir)
        else:
            self.dir_text.SetValue("./content")  # 默认导出目录

        if bitrate != "":
            self.bitrate_combo.SetValue(bitrate)
        else:
            self.bitrate_combo.SetValue("5000k")  # 默认码率

        if gpu_setting != "nan":
            self.gpu_combo.SetValue(gpu_setting)
        else:
            self.gpu_combo.SetValue("不使用GPU")  # 默认不使用GPU

        if delete_setting == "true":
            self.delete_combo.SetValue("删除原视频与音频")
        else:
            self.delete_combo.SetValue("保留原视频与音频")

        if export_format != "":
            self.export_format_combo.SetValue(export_format)
        else:
            self.export_format_combo.SetValue("mp4")

    def on_browse_dir(self, event):
        # 浏览文件夹对话框
        dlg = wx.DirDialog(self, "选择视频导出目录", style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.dir_text.SetValue(dlg.GetPath())
        dlg.Destroy()

    def on_ok(self, event):
        # 保存配置到文件
        export_dir = self.dir_text.GetValue()
        export_dir = export_dir.replace('\\', '/')
        # 如果目录路径包含冒号，则替换为短横线
        if ':' in export_dir:
            export_dir = export_dir.replace(':', '@-@')
        bitrate = self.bitrate_combo.GetValue()
        gpu_setting = self.gpu_combo.GetValue()

        # 获取是否删除原视频的设置
        delete_origin = self.delete_combo.GetValue()

        export_format = self.export_format_combo.GetValue()

        # 保存是否删除原视频的设置
        if delete_origin == "删除原视频与音频":
            update_properties_in_config("is_delete_origin", "true")
        else:
            update_properties_in_config("is_delete_origin", "false")

        # 保存到配置文件
        update_properties_in_config("export_dir", export_dir)
        update_properties_in_config("bitrate", bitrate)
        update_properties_in_config("export_format", export_format)
        if gpu_setting == "不使用GPU":
            update_properties_in_config("gpu_acceleration", "nan")
        else:
            update_properties_in_config("gpu_acceleration", gpu_setting)

        if '@-@' in export_dir:
            export_dir = export_dir.replace('@-@', ':')
        # 创建导出目录（如果不存在）
        if export_dir and not os.path.exists(export_dir):
            try:
                os.makedirs(export_dir)
            except Exception as e:
                wx.MessageBox(f"创建目录失败: {str(e)}", "错误", wx.OK | wx.ICON_ERROR)
                return

        self.EndModal(wx.ID_OK)


class BilibiliCrawlerApp(wx.App):
    def OnInit(self):
        frame = BilibiliCrawlerFrame()
        frame.Show()
        return True


if __name__ == '__main__':
    app = BilibiliCrawlerApp()
    app.MainLoop()
