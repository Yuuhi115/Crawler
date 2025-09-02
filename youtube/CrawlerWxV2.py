from youtube import *
import threading
import wx
import yt_dlp
import urllib.parse


class YouTubeDownloaderFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="YouTube Downloader", size=(600, 550))

        self.panel = wx.Panel(self)

        self.url_label = wx.StaticText(self.panel, label="视频URL:")
        self.url_text = wx.TextCtrl(self.panel)

        self.folder_label = wx.StaticText(self.panel, label="文件保存位置:")
        self.folder_text = wx.TextCtrl(self.panel)
        self.folder_btn = wx.Button(self.panel, label="Browse...")
        self.folder_btn.Bind(wx.EVT_BUTTON, self.on_browse)

        # 添加GPU选择选项
        self.gpu_label = wx.StaticText(self.panel, label="硬件加速选项:")
        self.gpu_choice = wx.Choice(self.panel, choices=["无硬件加速", "NVIDIA GPU", "AMD GPU"])
        self.gpu_choice.SetSelection(0)  # 默认选择无硬件加速

        self.start_btn = wx.Button(self.panel, label="开始下载")
        self.start_btn.Bind(wx.EVT_BUTTON, self.on_start)
        self.start_btn.SetForegroundColour(wx.Colour(0, 128, 0))

        # 添加日志窗口
        self.log_label = wx.StaticText(self.panel, label="日志:")
        self.log_text = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)

        self.progress_label = wx.StaticText(self.panel, label="下载进度:")
        self.progress_bar = wx.Gauge(self.panel, range=100)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.hsizer1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hsizer1.Add(self.folder_text, 1, wx.ALL | wx.EXPAND, 5)
        self.hsizer1.Add(self.folder_btn, 0, wx.ALL, 5)

        self.hsizer2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hsizer2.AddStretchSpacer(1)  # 添加弹性空间，将后续控件推到右边
        self.hsizer2.Add(self.start_btn, 0, wx.ALL, 5)

        # GPU选择器的布局
        self.hsizer3 = wx.BoxSizer(wx.HORIZONTAL)
        self.hsizer3.Add(self.gpu_label, 0, wx.ALL | wx.CENTER, 5)
        self.hsizer3.Add(self.gpu_choice, 0, wx.ALL, 5)

        self.sizer.Add(self.url_label, 0, wx.ALL, 5)
        self.sizer.Add(self.url_text, 0, wx.EXPAND | wx.ALL, 5)
        self.sizer.Add(self.folder_label, 0, wx.ALL, 5)
        self.sizer.Add(self.hsizer1, 0, wx.EXPAND | wx.ALL, 5)
        # 添加GPU选项到布局
        self.sizer.Add(self.hsizer3, 0, wx.ALL, 5)
        self.sizer.Add(self.progress_label, 0, wx.ALL, 5)
        self.sizer.Add(self.progress_bar, 0, wx.EXPAND | wx.ALL, 5)
        # 添加日志控件到布局中
        self.sizer.Add(self.log_label, 0, wx.ALL, 5)
        self.sizer.Add(self.log_text, 1, wx.EXPAND | wx.ALL, 5)

        self.sizer.Add(self.hsizer2, 0, wx.EXPAND | wx.ALL, 5)

        self.panel.SetSizer(self.sizer)
        self.Show()

    def log_message(self, message):
        """在日志窗口中添加消息"""
        wx.CallAfter(self.log_text.AppendText, message + '\n')

    def on_browse(self, event):
        dlg = wx.DirDialog(self, "Choose a directory", style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.folder_text.SetValue(dlg.GetPath())
        dlg.Destroy()

    def on_start(self, event):
        url = self.url_text.GetValue()
        save_folder = self.folder_text.GetValue()

        download_thread = threading.Thread(target=self.download_video, args=(url, save_folder))
        download_thread.start()

    def download_video(self, url, save_folder):
        try:
            # 创建自定义日志记录器
            class YTDLPLogger:
                def __init__(self, frame):
                    self.frame = frame

                def debug(self, msg):
                    if not msg.startswith('[debug]'):
                        self.frame.log_message(msg)

                def warning(self, msg):
                    self.frame.log_message(f"[WARNING] {msg}")

                def error(self, msg):
                    self.frame.log_message(f"[ERROR] {msg}")

            # 获取用户选择的GPU选项
            gpu_selection = self.gpu_choice.GetSelection()
            gpu_options = ["无硬件加速", "NVIDIA GPU", "AMD GPU"]
            selected_gpu = gpu_options[gpu_selection]

            self.log_message(f"DEVICE: {selected_gpu}")

            # 基础选项
            options = {
                'outtmpl': save_folder + '/%(title)s.%(ext)s',
                'progress_hooks': [self.update_progress],
                'logger': YTDLPLogger(self),  # 使用自定义日志记录器
                'format': 'bestvideo+bestaudio/mp4',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4'
                }]
            }

            # 根据用户选择配置硬件加速
            if selected_gpu == "NVIDIA GPU":
                postprocessor_args = {
                    'ffmpeg': [
                        '-c:v', 'h264_nvenc',  # NVIDIA编码器
                    ]
                }
                # 添加到现有的postprocessor_args而不是覆盖整个postprocessors
                options['postprocessor_args'] = postprocessor_args
                self.log_message("NVIDIA GPU Acceleration ON")

            elif selected_gpu == "AMD GPU":
                postprocessor_args = {
                    'ffmpeg': [
                        '-c:v', 'h264_amf',  # AMD编码器
                    ]
                }
                # 添加到现有的postprocessor_args而不是覆盖整个postprocessors
                options['postprocessor_args'] = postprocessor_args
                self.log_message("AMD GPU Acceleration ON")

            self.log_message("Starting download...")
            with yt_dlp.YoutubeDL(options) as ydl:
                video_info = ydl.extract_info(url, download=False)
                self.log_message(f"Video Title: {video_info.get('title', 'Unknown')}")
                self.log_message(f"Uploader: {video_info.get('uploader', 'Unknown')}")
                self.log_message("Downloading...")

                if 'uploader' in video_info and 'youtube' in urllib.parse.urlparse(url).netloc:
                    ydl.download([url])
                else:
                    ydl.download([url])

            self.log_message("Download completed!")
            wx.CallAfter(wx.MessageBox, '下载完毕!', 'Info', wx.OK | wx.ICON_INFORMATION)

        except Exception as e:
            error_msg = f'Download error occurred: {str(e)}'
            self.log_message(error_msg)
            wx.CallAfter(wx.MessageBox, error_msg, 'Error', wx.OK | wx.ICON_ERROR)

    def update_progress(self, progress):
        if 'total_bytes' in progress and 'downloaded_bytes' in progress:
            percentage = int(progress['downloaded_bytes'] * 100 / progress['total_bytes'])
            wx.CallAfter(self.progress_bar.SetValue, percentage)
            if progress['status'] == 'downloading':
                self.log_message(f"Download Progress: {percentage}%")
            elif progress['status'] == 'finished':
                self.log_message("Downloading finished! Video format converting...")


app = wx.App()
frame = YouTubeDownloaderFrame()
app.MainLoop()
