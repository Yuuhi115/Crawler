import wx
from utils import read_properties_from_config, update_properties_in_config
from get_proxy import *
import threading


class ProxyConfigDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="代理设置", size=(450, 300))
        self.parent = parent
        self.setup_ui()
        self.load_config()
        self.Center()

    def setup_ui(self):
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # 代理开关
        proxy_enable_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.proxy_enable_checkbox = wx.CheckBox(panel, label="启用代理")
        self.proxy_enable_checkbox.Bind(wx.EVT_CHECKBOX, self.on_proxy_enable)
        proxy_enable_sizer.Add(self.proxy_enable_checkbox, 0, wx.ALL, 5)
        main_sizer.Add(proxy_enable_sizer, 0, wx.EXPAND)

        # 代理设置区域
        proxy_box = wx.StaticBox(panel, label="代理配置")
        proxy_sizer = wx.StaticBoxSizer(proxy_box, wx.VERTICAL)

        # 代理IP选择
        ip_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ip_sizer.Add(wx.StaticText(panel, label="代理IP:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.ip_combo = wx.ComboBox(panel, style=wx.CB_DROPDOWN)
        ip_sizer.Add(self.ip_combo, 1, wx.EXPAND | wx.ALL, 5)
        proxy_sizer.Add(ip_sizer, 0, wx.EXPAND)

        # 代理端口
        port_sizer = wx.BoxSizer(wx.HORIZONTAL)
        port_sizer.Add(wx.StaticText(panel, label="端口:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.port_text = wx.TextCtrl(panel)
        port_sizer.Add(self.port_text, 1, wx.EXPAND | wx.ALL, 5)
        proxy_sizer.Add(port_sizer, 0, wx.EXPAND)

        main_sizer.Add(proxy_sizer, 0, wx.EXPAND | wx.ALL, 5)

        tip_sizer = wx.BoxSizer(wx.HORIZONTAL)
        tip_sizer.Add(wx.StaticText(panel, label="提示：本软件获取的代理几乎不可用，如需设置代理，请自行输入可用代理"),
                      0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        tip_sizer.Add(wx.StaticText(panel, label=""), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        main_sizer.Add(tip_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # 代理列表操作区域
        action_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.refresh_btn = wx.Button(panel, label="刷新代理列表")
        self.refresh_btn.Bind(wx.EVT_BUTTON, self.on_refresh)
        action_sizer.Add(self.refresh_btn, 0, wx.ALL, 5)

        self.test_btn = wx.Button(panel, label="测试连接")
        self.test_btn.Bind(wx.EVT_BUTTON, self.on_test)
        action_sizer.Add(self.test_btn, 0, wx.ALL, 5)

        main_sizer.Add(action_sizer, 0, wx.ALIGN_CENTER)

        # 按钮区域
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ok_btn = wx.Button(panel, wx.ID_OK, label="确定")
        self.ok_btn.Bind(wx.EVT_BUTTON, self.on_ok)
        button_sizer.Add(self.ok_btn, 0, wx.ALL, 5)

        self.cancel_btn = wx.Button(panel, wx.ID_CANCEL, label="取消")
        button_sizer.Add(self.cancel_btn, 0, wx.ALL, 5)

        main_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER)

        panel.SetSizer(main_sizer)

        # 初始化控件状态
        self.update_controls_state()

    def update_controls_state(self):
        """根据代理启用状态更新控件可用性"""
        enabled = self.proxy_enable_checkbox.GetValue()
        self.ip_combo.Enable(enabled)
        self.port_text.Enable(enabled)
        self.refresh_btn.Enable(enabled)
        self.test_btn.Enable(enabled)

    def on_proxy_enable(self, event):
        """代理启用状态改变事件"""
        self.update_controls_state()

    def load_config(self):
        """从配置文件加载代理设置"""
        # 读取代理启用状态
        proxy_enabled = read_properties_from_config("proxy_enabled")
        self.proxy_enable_checkbox.SetValue(proxy_enabled == "true")

        # 读取代理配置
        proxy_ip = read_properties_from_config("proxy_ip")
        proxy_port = read_properties_from_config("proxy_port")

        # 设置控件值
        self.port_text.SetValue(proxy_port if proxy_port != "nan" else "")

        # 加载代理IP列表
        self.load_proxy_list()

        # 设置当前选中的IP
        if proxy_ip != "nan":
            self.ip_combo.SetValue(proxy_ip)

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
                    self.ip_combo.Clear()
                    # 添加IP到下拉列表
                    for index, row in df.iterrows():
                        ip = row['IP']
                        port = row['PORT']
                        # 将IP和端口组合显示
                        display_text = f"{ip}:{port}"
                        self.ip_combo.Append(display_text, ip)
                    return True
            except Exception as e:
                wx.MessageBox(f"加载代理列表失败: {str(e)}", "错误", wx.OK | wx.ICON_ERROR)
        else:
            # 如果代理文件不存在，添加一个提示项
            self.ip_combo.Append("未找到代理列表文件", "")
        return False

    def on_refresh(self, event):
        """刷新代理列表"""
        print("开始刷新代理列表...")
        refresh_thread = threading.Thread(target=self.refresh_worker)
        refresh_thread.daemon = True
        refresh_thread.start()

    def refresh_worker(self):
        create_proxies_table_csv()
        if self.load_proxy_list():
            wx.MessageBox("代理列表刷新成功", "提示", wx.OK | wx.ICON_INFORMATION)
        else:
            wx.MessageBox("代理列表刷新失败，请检查代理文件", "错误", wx.OK | wx.ICON_ERROR)

    def on_test(self, event):
        """测试代理连接"""
        print("开始测试代理连接...")
        test_thread = threading.Thread(target=self.test_worker)
        test_thread.daemon = True
        test_thread.start()

    def test_worker(self):
        """测试代理连接"""
        if not self.proxy_enable_checkbox.GetValue():
            wx.MessageBox("请先启用代理", "提示", wx.OK | wx.ICON_WARNING)
            return

        ip_port = self.ip_combo.GetValue()
        if not ip_port:
            wx.MessageBox("请选择代理IP", "提示", wx.OK | wx.ICON_WARNING)
            return

        # 解析IP和端口
        if ':' in ip_port:
            ip, port = ip_port.split(':', 1)
        else:
            ip = ip_port
            port = self.port_text.GetValue()

        if not port:
            wx.MessageBox("请输入端口号", "提示", wx.OK | wx.ICON_WARNING)
            return

        # 这里应该添加实际的连接测试逻辑
        # wx.MessageBox(f"代理连接测试功能待实现\nIP: {ip}\n端口: {port}", "提示", wx.OK | wx.ICON_INFORMATION)
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
                wx.MessageBox("代理连接成功", "提示", wx.OK | wx.ICON_INFORMATION)
            else:
                wx.MessageBox("代理连接失败", "提示", wx.OK | wx.ICON_ERROR)
        except Exception as e:
            wx.MessageBox(f"代理连接失败: {str(e)}", "错误", wx.OK | wx.ICON_ERROR)

    def on_ok(self, event):
        """确定按钮事件"""
        # 保存配置
        update_properties_in_config("proxy_enabled", "true" if self.proxy_enable_checkbox.GetValue() else "false")

        # 获取选中的IP
        ip_port = self.ip_combo.GetValue()
        ip = ""
        port = self.port_text.GetValue()

        if ip_port and ':' in ip_port:
            ip, port = ip_port.split(':', 1)
        elif ip_port:
            ip = ip_port

        # 保存代理配置
        update_properties_in_config("proxy_ip", ip if ip else "NaN")
        update_properties_in_config("proxy_port", port if port else "NaN")

        self.EndModal(wx.ID_OK)
