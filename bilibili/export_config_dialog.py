import wx
from utils import *
import os
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