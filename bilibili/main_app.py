import wx
import threading
import os
from fetch_site import run_crawler_login, run_search_page
from proxy_config_dialog import ProxyConfigDialog
from fetch_video import run_video_crawler
from utils import *
import sys


class BilibiliCrawlerFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="Bilibili视频下载器", size=(600, 500))
        self.panel = wx.Panel(self)
        self.cookie_expiry = None
        self.create_ui()
        self.SetMinSize((500, 400))
        self.Center()

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

        search_other_H_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.search_btn = wx.Button(self.panel, label="搜索视频")
        self.search_btn.Bind(wx.EVT_BUTTON, self.on_search)

        self.export_config_btn = wx.Button(self.panel, label="导出设置")
        self.export_config_btn.Bind(wx.EVT_BUTTON, self.on_config)

        self.proxy_config_btn = wx.Button(self.panel, label="代理设置")
        self.proxy_config_btn.Bind(wx.EVT_BUTTON, self.on_proxy_config)

        search_other_H_sizer.Add(self.search_btn, 0, wx.ALL, 5)
        search_other_H_sizer.Add(self.export_config_btn, 0, wx.ALL, 5)
        search_other_H_sizer.Add(self.proxy_config_btn, 0, wx.ALL, 5)

        search_sizer.Add(search_other_H_sizer, 0, wx.EXPAND)

        main_sizer.Add(search_sizer, 0, wx.EXPAND | wx.ALL, 5)

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

        video_sizer.Add(url_sizer, 0, wx.EXPAND)
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
