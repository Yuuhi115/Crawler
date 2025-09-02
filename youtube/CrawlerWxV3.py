from youtube import *



class YouTubeDownloaderFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="YouTube Downloader - GPU Accelerated", size=(700, 600))

        self.panel = wx.Panel(self)

        self.url_label = wx.StaticText(self.panel, label="视频URL:")
        self.url_text = wx.TextCtrl(self.panel)

        self.folder_label = wx.StaticText(self.panel, label="文件保存位置:")
        self.folder_text = wx.TextCtrl(self.panel)
        self.folder_btn = wx.Button(self.panel, label="Browse...")
        self.folder_btn.Bind(wx.EVT_BUTTON, self.on_browse)

        # 添加GPU加速选项
        self.gpu_label = wx.StaticText(self.panel, label="GPU加速:")
        self.gpu_choice = wx.Choice(self.panel,
                                    choices=["自动检测", "NVIDIA (NVENC)", "AMD (AMF)", "Intel (QSV)", "禁用GPU"])
        self.gpu_choice.SetSelection(0)

        # 添加输出格式选择
        self.format_label = wx.StaticText(self.panel, label="输出格式:")
        self.format_choice = wx.Choice(self.panel, choices=["MP4", "MKV", "AVI", "MOV"])
        self.format_choice.SetSelection(0)

        # 添加质量设置
        self.quality_label = wx.StaticText(self.panel, label="视频质量:")
        self.quality_choice = wx.Choice(self.panel, choices=["最佳质量", "高质量", "中等质量", "快速压缩"])
        self.quality_choice.SetSelection(0)

        self.start_btn = wx.Button(self.panel, label="开始下载")
        self.start_btn.Bind(wx.EVT_BUTTON, self.on_start)
        self.start_btn.SetForegroundColour(wx.Colour(0, 128, 0))

        # GPU状态检测按钮
        self.detect_btn = wx.Button(self.panel, label="检测GPU支持")
        self.detect_btn.Bind(wx.EVT_BUTTON, self.on_detect_gpu)
        self.detect_btn.SetForegroundColour(wx.Colour(0, 0, 128))

        # 添加日志窗口
        self.log_label = wx.StaticText(self.panel, label="日志:")
        self.log_text = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)

        self.progress_label = wx.StaticText(self.panel, label="下载进度:")
        self.progress_bar = wx.Gauge(self.panel, range=100)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # 文件夹选择布局
        self.hsizer1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hsizer1.Add(self.folder_text, 1, wx.ALL | wx.EXPAND, 5)
        self.hsizer1.Add(self.folder_btn, 0, wx.ALL, 5)

        # GPU和格式选择布局
        self.hsizer_gpu = wx.BoxSizer(wx.HORIZONTAL)
        self.hsizer_gpu.Add(self.gpu_label, 0, wx.ALL | wx.CENTER, 5)
        self.hsizer_gpu.Add(self.gpu_choice, 1, wx.ALL | wx.EXPAND, 5)
        self.hsizer_gpu.Add(self.detect_btn, 0, wx.ALL, 5)

        self.hsizer_format = wx.BoxSizer(wx.HORIZONTAL)
        self.hsizer_format.Add(self.format_label, 0, wx.ALL | wx.CENTER, 5)
        self.hsizer_format.Add(self.format_choice, 1, wx.ALL | wx.EXPAND, 5)
        self.hsizer_format.Add(self.quality_label, 0, wx.ALL | wx.CENTER, 5)
        self.hsizer_format.Add(self.quality_choice, 1, wx.ALL | wx.EXPAND, 5)

        # 按钮布局
        self.hsizer2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hsizer2.AddStretchSpacer(1)
        self.hsizer2.Add(self.start_btn, 0, wx.ALL, 5)

        # 主布局
        self.sizer.Add(self.url_label, 0, wx.ALL, 5)
        self.sizer.Add(self.url_text, 0, wx.EXPAND | wx.ALL, 5)
        self.sizer.Add(self.folder_label, 0, wx.ALL, 5)
        self.sizer.Add(self.hsizer1, 0, wx.EXPAND | wx.ALL, 5)
        self.sizer.Add(self.hsizer_gpu, 0, wx.EXPAND | wx.ALL, 5)
        self.sizer.Add(self.hsizer_format, 0, wx.EXPAND | wx.ALL, 5)
        self.sizer.Add(self.progress_label, 0, wx.ALL, 5)
        self.sizer.Add(self.progress_bar, 0, wx.EXPAND | wx.ALL, 5)
        self.sizer.Add(self.log_label, 0, wx.ALL, 5)
        self.sizer.Add(self.log_text, 1, wx.EXPAND | wx.ALL, 5)
        self.sizer.Add(self.hsizer2, 0, wx.EXPAND | wx.ALL, 5)

        self.panel.SetSizer(self.sizer)
        self.Show()

    def log_message(self, message):
        """在日志窗口中添加消息"""
        wx.CallAfter(self.log_text.AppendText, message + '\n')

    def detect_gpu_support(self):
        """检测可用的GPU编码器"""
        gpu_encoders = []

        try:
            # 检测NVIDIA GPU (NVENC)
            result = subprocess.run(['ffmpeg', '-hide_banner', '-encoders'],
                                    capture_output=True, text=True, timeout=10)
            output = result.stdout

            if 'h264_nvenc' in output:
                gpu_encoders.append('NVIDIA')
            if 'h264_amf' in output:
                gpu_encoders.append('AMD')
            if 'h264_qsv' in output:
                gpu_encoders.append('Intel')

        except Exception as e:
            self.log_message(f"GPU检测错误: {str(e)}")

        return gpu_encoders

    def on_detect_gpu(self, event):
        """检测GPU支持按钮事件"""
        self.log_message("正在检测GPU支持...")
        available_gpus = self.detect_gpu_support()

        if available_gpus:
            gpu_info = "检测到以下GPU编码器: " + ", ".join(available_gpus)
            self.log_message(gpu_info)
            wx.MessageBox(gpu_info, 'GPU检测结果', wx.OK | wx.ICON_INFORMATION)
        else:
            self.log_message("未检测到GPU硬件编码器支持")
            wx.MessageBox('未检测到GPU硬件编码器支持\n将使用CPU编码', 'GPU检测结果', wx.OK | wx.ICON_WARNING)

    def get_gpu_encoder_config(self):
        """根据选择获取GPU编码器配置"""
        gpu_selection = self.gpu_choice.GetSelection()
        quality_selection = self.quality_choice.GetSelection()

        # 质量参数映射 - 调整为更兼容的值
        quality_configs = {
            0: {'crf': '20', 'preset': 'medium'},  # 最佳质量
            1: {'crf': '23', 'preset': 'medium'},  # 高质量
            2: {'crf': '28', 'preset': 'fast'},  # 中等质量
            3: {'crf': '30', 'preset': 'fast'}  # 快速压缩
        }

        quality_config = quality_configs[quality_selection]

        if gpu_selection == 0:  # 自动检测
            available_gpus = self.detect_gpu_support()
            if 'NVIDIA' in available_gpus:
                return self.get_nvenc_config(quality_config)
            elif 'AMD' in available_gpus:
                return self.get_amf_config(quality_config)
            elif 'Intel' in available_gpus:
                return self.get_qsv_config(quality_config)
            else:
                return self.get_cpu_config(quality_config)
        elif gpu_selection == 1:  # NVIDIA
            return self.get_nvenc_config(quality_config)
        elif gpu_selection == 2:  # AMD
            return self.get_amf_config(quality_config)
        elif gpu_selection == 3:  # Intel
            return self.get_qsv_config(quality_config)
        else:  # 禁用GPU
            return self.get_cpu_config(quality_config)

    def get_nvenc_config(self, quality_config):
        """NVIDIA NVENC配置"""
        return [
            '-c:v', 'h264_nvenc',
            '-preset', 'medium',
            '-cq', quality_config['crf'],
            '-c:a', 'copy'
        ]

    def get_amf_config(self, quality_config):
        """AMD AMF配置"""
        return [
            '-c:v', 'h264_amf',
            '-quality', 'speed',
            '-rc', 'cqp',
            '-qp_i', quality_config['crf'],
            '-c:a', 'copy'
        ]

    def get_qsv_config(self, quality_config):
        """Intel QSV配置"""
        return [
            '-c:v', 'h264_qsv',
            '-preset', 'medium',
            '-q', quality_config['crf'],
            '-c:a', 'copy'
        ]

    def get_cpu_config(self, quality_config):
        """CPU编码配置"""
        return [
            '-c:v', 'libx264',
            '-preset', quality_config['preset'],
            '-crf', quality_config['crf'],
            '-c:a', 'copy'
        ]

    def on_browse(self, event):
        dlg = wx.DirDialog(self, "Choose a directory", style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.folder_text.SetValue(dlg.GetPath())
        dlg.Destroy()

    def on_start(self, event):
        url = self.url_text.GetValue()
        save_folder = self.folder_text.GetValue()

        if not url:
            wx.MessageBox('请输入视频URL!', 'Error', wx.OK | wx.ICON_ERROR)
            return

        if not save_folder:
            wx.MessageBox('请选择保存文件夹!', 'Error', wx.OK | wx.ICON_ERROR)
            return

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

            # 获取输出格式
            format_selection = self.format_choice.GetSelection()
            output_formats = ['mp4', 'mkv', 'avi', 'mov']
            output_format = output_formats[format_selection]

            # 获取GPU编码器配置
            encoder_config = self.get_gpu_encoder_config()

            # 构建yt-dlp选项 - 使用更简单的配置
            options = {
                'outtmpl': save_folder + '/%(title)s.%(ext)s',
                'progress_hooks': [self.update_progress],
                'logger': YTDLPLogger(self),
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
            }

            # 只有在需要格式转换时才添加后处理器
            if output_format != 'mp4' or self.gpu_choice.GetSelection() != 4:
                options['postprocessors'] = [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': output_format,

                }]
                options['postprocessor_args'].append(encoder_config)

            # 记录使用的编码器信息
            gpu_selection = self.gpu_choice.GetSelection()
            gpu_options = ["自动检测", "NVIDIA (NVENC)", "AMD (AMF)", "Intel (QSV)", "禁用GPU"]
            self.log_message(f"使用编码器: {gpu_options[gpu_selection]}")
            self.log_message(f"输出格式: {output_format.upper()}")
            self.log_message("开始下载...")

            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([url])

            self.log_message("下载和转换完成!")
            wx.CallAfter(wx.MessageBox, '下载完毕!', 'Info', wx.OK | wx.ICON_INFORMATION)

        except Exception as e:
            error_msg = f'下载错误: {str(e)}'
            self.log_message(error_msg)
            wx.CallAfter(wx.MessageBox, f'下载错误!: {str(e)}', 'Error', wx.OK | wx.ICON_ERROR)

    def update_progress(self, progress):
        if 'total_bytes' in progress and 'downloaded_bytes' in progress:
            percentage = int(progress['downloaded_bytes'] * 100 / progress['total_bytes'])
            wx.CallAfter(self.progress_bar.SetValue, percentage)
            if progress['status'] == 'downloading':
                self.log_message(f"下载进度: {percentage}%")
            elif progress['status'] == 'finished':
                self.log_message("下载完成，开始GPU加速格式转换...")
        elif progress['status'] == 'processing':
            self.log_message("正在使用GPU加速处理视频...")


if __name__ == '__main__':
    app = wx.App()
    frame = YouTubeDownloaderFrame()
    app.MainLoop()