import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from utils import read_properties_from_config, update_properties_in_config
import os
from tkinter import filedialog


class ExportConfigDialog:
    def __init__(self, parent):
        self.parent = parent
        self.top = ttk.Toplevel(parent)
        self.top.title("导出设置")
        self.top.geometry("400x500")
        self.top.transient(parent)
        self.top.grab_set()

        self.setup_ui()
        self.load_config()
        self.center_window()

    def center_window(self):
        self.top.update_idletasks()
        width = self.top.winfo_width()
        height = self.top.winfo_height()
        x = (self.top.winfo_screenwidth() // 2) - (width // 2)
        y = (self.top.winfo_screenheight() // 2) - (height // 2)
        self.top.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.top, padding=10)
        main_frame.pack(fill=BOTH, expand=YES)

        # 视频导出目录设置
        dir_frame = ttk.LabelFrame(main_frame, text="视频导出目录", padding=10)
        dir_frame.pack(fill=X, pady=(0, 10))

        dir_input_frame = ttk.Frame(dir_frame)
        dir_input_frame.pack(fill=X)

        self.dir_text = ttk.Entry(dir_input_frame)
        self.dir_text.pack(side=LEFT, fill=X, expand=YES, padx=(0, 5))

        self.dir_btn = ttk.Button(dir_input_frame, text="选择目录...", command=self.on_browse_dir)
        self.dir_btn.pack(side=LEFT)

        # 视频码率设置
        bitrate_frame = ttk.LabelFrame(main_frame, text="视频码率设置", padding=10)
        bitrate_frame.pack(fill=X, pady=(0, 10))

        bitrate_choices = ["1000k", "2000k", "3000k", "4000k", "5000k", "6000k", "7000k", "8000k"]
        self.bitrate_combo = ttk.Combobox(bitrate_frame, values=bitrate_choices, state="readonly")
        self.bitrate_combo.pack(fill=X)

        # GPU加速选择
        gpu_frame = ttk.LabelFrame(main_frame, text="GPU加速设置", padding=10)
        gpu_frame.pack(fill=X, pady=(0, 10))

        gpu_choices = ["不使用GPU", "NVIDIA", "AMD", "Intel"]
        self.gpu_combo = ttk.Combobox(gpu_frame, values=gpu_choices, state="readonly")
        self.gpu_combo.pack(fill=X)

        # 是否删除原视频
        delete_frame = ttk.LabelFrame(main_frame, text="删除原视频设置", padding=10)
        delete_frame.pack(fill=X, pady=(0, 10))

        delete_choices = ["删除原视频与音频", "保留原视频与音频"]
        self.delete_combo = ttk.Combobox(delete_frame, values=delete_choices, state="readonly")
        self.delete_combo.pack(fill=X)

        # 导出格式设置
        export_format_frame = ttk.LabelFrame(main_frame, text="导出格式设置", padding=10)
        export_format_frame.pack(fill=X, pady=(0, 10))

        self.export_format_combo = ttk.Combobox(export_format_frame, values=["mp4", "mp3"], state="readonly")
        self.export_format_combo.pack(fill=X)

        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=X, pady=(10, 0))

        self.ok_btn = ttk.Button(button_frame, text="确定", bootstyle=SUCCESS, command=self.on_ok)
        self.ok_btn.pack(side=LEFT, padx=(0, 5))

        self.cancel_btn = ttk.Button(button_frame, text="取消", bootstyle=SECONDARY, command=self.top.destroy)
        self.cancel_btn.pack(side=LEFT)

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
            self.dir_text.insert(0, export_dir)
        else:
            self.dir_text.insert(0, "./content")  # 默认导出目录

        if bitrate != "":
            self.bitrate_combo.set(bitrate)
        else:
            self.bitrate_combo.set("5000k")  # 默认码率

        if gpu_setting != "nan":
            self.gpu_combo.set(gpu_setting)
        else:
            self.gpu_combo.set("不使用GPU")  # 默认不使用GPU

        if delete_setting == "true":
            self.delete_combo.set("删除原视频与音频")
        else:
            self.delete_combo.set("保留原视频与音频")

        if export_format != "":
            self.export_format_combo.set(export_format)
        else:
            self.export_format_combo.set("mp4")

    def on_browse_dir(self):
        # 浏览文件夹对话框
        dir_path = filedialog.askdirectory(title="选择视频导出目录")
        if dir_path:
            self.dir_text.delete(0, END)
            self.dir_text.insert(0, dir_path)

    def on_ok(self):
        # 保存配置到文件
        export_dir = self.dir_text.get()
        export_dir = export_dir.replace('\\', '/')
        # 如果目录路径包含冒号，则替换为短横线
        if ':' in export_dir:
            export_dir = export_dir.replace(':', '@-@')
        bitrate = self.bitrate_combo.get()
        gpu_setting = self.gpu_combo.get()

        # 获取是否删除原视频的设置
        delete_origin = self.delete_combo.get()

        export_format = self.export_format_combo.get()

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
                from ttkbootstrap.dialogs import Messagebox
                Messagebox.show_error(f"创建目录失败: {str(e)}", "错误")
                return

        self.top.destroy()

    def show(self):
        self.top.mainloop()
