import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from utils import read_properties_from_config, update_properties_in_config
from get_proxy import *
import threading
import os
import pandas as pd


class ProxyConfigDialog:
    def __init__(self, parent):
        self.parent = parent
        self.top = ttk.Toplevel(parent)
        self.top.title("代理设置")
        self.top.geometry("450x300")
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
        main_frame.pack(fill="both", expand=YES)

        # 代理开关
        self.proxy_enable_var = ttk.BooleanVar()
        proxy_enable_frame = ttk.Frame(main_frame)
        proxy_enable_frame.pack(fill="x", pady=(0, 10))
        self.proxy_enable_checkbox = ttk.Checkbutton(
            proxy_enable_frame,
            text="启用代理",
            variable=self.proxy_enable_var,
            command=self.on_proxy_enable
        )
        self.proxy_enable_checkbox.pack(anchor="w")

        # 代理设置区域
        proxy_frame = ttk.LabelFrame(main_frame, text="代理配置", padding=10)
        proxy_frame.pack(fill="x", pady=(0, 10))

        # 代理IP选择
        ip_frame = ttk.Frame(proxy_frame)
        ip_frame.pack(fill="x", pady=(0, 5))
        ttk.Label(ip_frame, text="代理IP:").pack(side="left")
        self.ip_combo = ttk.Combobox(ip_frame, state="readonly")
        self.ip_combo.pack(side="left", fill="x", expand=YES, padx=(5, 0))

        # 代理端口
        # port_frame = ttk.Frame(proxy_frame)
        # port_frame.pack(fill="x", pady=(0, 5))
        # ttk.Label(port_frame, text="端口:").pack(side="left")
        # self.port_text = ttk.Entry(port_frame)
        # self.port_text.pack(side="left", fill="x", expand=YES, padx=(5, 0))

        # 提示信息
        tip_frame = ttk.Frame(main_frame)
        tip_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(
            tip_frame,
            text="提示：本软件获取的代理几乎不可用，如需设置代理，请自行输入可用代理",
            foreground="orange"
        ).pack()

        # 代理列表操作区域
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill="x", pady=(0, 10))

        self.refresh_btn = ttk.Button(action_frame, text="刷新代理列表", command=self.on_refresh)
        self.refresh_btn.pack(side="left", padx=(0, 5))

        self.test_btn = ttk.Button(action_frame, text="测试连接", command=self.on_test)
        self.test_btn.pack(side="left", padx=(0, 5))

        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")

        self.ok_btn = ttk.Button(button_frame, text="确定", bootstyle="success", command=self.on_ok)
        self.ok_btn.pack(side="left", padx=(0, 5))

        self.cancel_btn = ttk.Button(button_frame, text="取消", bootstyle="secondary", command=self.top.destroy)
        self.cancel_btn.pack(side="left")

        # 初始化控件状态
        self.update_controls_state()

    def update_controls_state(self):
        """根据代理启用状态更新控件可用性"""
        enabled = self.proxy_enable_var.get()
        state = NORMAL if enabled else DISABLED
        self.ip_combo.configure(state=state if enabled else "readonly")
        # self.port_text.configure(state=state)
        self.refresh_btn.configure(state=state)
        self.test_btn.configure(state=state)

    def on_proxy_enable(self):
        """代理启用状态改变事件"""
        self.update_controls_state()

    def load_config(self):
        """从配置文件加载代理设置"""
        # 读取代理启用状态
        proxy_enabled = read_properties_from_config("proxy_enabled")
        self.proxy_enable_var.set(proxy_enabled == "true")

        # 读取代理配置
        proxy_ip = read_properties_from_config("proxy_ip")
        proxy_port = read_properties_from_config("proxy_port")

        # 设置控件值
        # self.port_text.delete(0, END)
        # if proxy_port != "NaN":
        #     self.port_text.insert(0, proxy_port)

        # 加载代理IP列表
        self.load_proxy_list()

        # 设置当前选中的IP
        if proxy_ip != "nan":
            self.ip_combo.set(f"{proxy_ip}:{proxy_port}")

        # 更新控件状态
        self.update_controls_state()

    def load_proxy_list(self):
        """从CSV文件加载代理IP列表"""
        proxy_csv_path = "./app_config/proxy_ip_china.csv"
        if os.path.exists(resource_path(proxy_csv_path)):
            try:
                df = pd.read_csv(resource_path(proxy_csv_path))
                if not df.empty:
                    # 清空现有项目
                    self.ip_combo['values'] = ()
                    # 添加IP到下拉列表
                    values = []
                    for index, row in df.iterrows():
                        ip = row['IP']
                        port = row['PORT']
                        # 将IP和端口组合显示
                        display_text = f"{ip}:{port}"
                        values.append(display_text)
                    self.ip_combo['values'] = values
                    return True
            except Exception as e:
                Messagebox.show_error(f"加载代理列表失败: {str(e)}", "错误")
        else:
            # 如果代理文件不存在，添加一个提示项
            self.ip_combo['values'] = ("未找到代理列表文件",)
        return False

    def on_refresh(self):
        """刷新代理列表"""
        print("开始刷新代理列表...")
        refresh_thread = threading.Thread(target=self.refresh_worker)
        refresh_thread.daemon = True
        refresh_thread.start()

    def refresh_worker(self):
        create_proxies_table_csv()
        if self.load_proxy_list():
            self.top.after(0, lambda: Messagebox.show_info("代理列表刷新成功", "提示"))
        else:
            self.top.after(0, lambda: Messagebox.show_error("代理列表刷新失败，请检查代理文件", "错误"))

    def on_test(self):
        """测试代理连接"""
        print("开始测试代理连接...")
        test_thread = threading.Thread(target=self.test_worker)
        test_thread.daemon = True
        test_thread.start()

    def test_worker(self):
        """测试代理连接"""
        if not self.proxy_enable_var.get():
            self.top.after(0, lambda: Messagebox.show_warning("请先启用代理", "提示"))
            return

        ip_port = self.ip_combo.get()
        if not ip_port:
            self.top.after(0, lambda: Messagebox.show_warning("请选择代理IP", "提示"))
            return

        # 解析IP和端口
        if ':' in ip_port:
            ip, port = ip_port.split(':', 1)
        else:
            ip = ip_port
            # port = self.port_text.get()
            port = "NaN"

        if not port or port != "NaN":
            self.top.after(0, lambda: Messagebox.show_warning("请输入端口号", "提示"))
            return

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
        }
        proxy_url = f"http://{ip}:{port}"
        print(f"代理地址：{proxy_url}")
        proxies = {
            "http": proxy_url,
            "https": proxy_url
        }
        try:
            response = requests.get(url="https://www.baidu.com/", headers=headers, proxies=proxies, timeout=3)
            print(f"测试连接返回状态码:{response.status_code}")
            if response.status_code == 200:
                self.top.after(0, lambda: Messagebox.show_info("代理连接成功", "提示"))
            else:
                self.top.after(0, lambda: Messagebox.show_error("代理连接失败", "提示"))
        except Exception as e:
            self.top.after(0, lambda: Messagebox.show_error(f"代理连接失败: {str(e)}", "错误"))

    def on_ok(self):
        """确定按钮事件"""
        # 保存配置
        update_properties_in_config("proxy_enabled", "true" if self.proxy_enable_var.get() else "false")

        # 获取选中的IP
        ip_port = self.ip_combo.get()
        ip = ""
        port = ""
        # port = self.port_text.get()

        if ip_port and ':' in ip_port:
            ip, port = ip_port.split(':', 1)
        elif ip_port:
            ip = ip_port
            port = "NaN"

        # 保存代理配置
        update_properties_in_config("proxy_ip", ip if ip else "NaN")
        update_properties_in_config("proxy_port", port if port else "NaN")

        self.top.destroy()

    def show(self):
        self.top.mainloop()
