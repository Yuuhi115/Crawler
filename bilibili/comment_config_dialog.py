import wx
import os
from utils import *

# comment_config_dialog.py
class CommentConfigDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="评论获取设置", size=(250, 200))
        self.panel = wx.Panel(self)
        self.init_ui()
        self.load_config()
        self.Center()

    def init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # 评论最大页数设置
        max_pages_sizer = wx.BoxSizer(wx.HORIZONTAL)
        max_pages_sizer.Add(wx.StaticText(self.panel, label="获取评论最大页数(1页20条):"), 0,
                            wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.max_pages_ctrl = wx.SpinCtrl(self.panel, value="10", min=1, max=1000)
        max_pages_sizer.Add(self.max_pages_ctrl, 0, wx.ALL, 5)
        main_sizer.Add(max_pages_sizer, 0, wx.EXPAND)

        # 是否获取子评论设置
        sub_comment_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sub_comment_sizer.Add(wx.StaticText(self.panel, label="是否获取子评论:"), 0,
                              wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.sub_comment_choice = wx.RadioBox(self.panel, label="",
                                              choices=["是", "否"],
                                              majorDimension=1,
                                              style=wx.RA_SPECIFY_ROWS)
        sub_comment_sizer.Add(self.sub_comment_choice, 0, wx.ALL, 5)
        main_sizer.Add(sub_comment_sizer, 0, wx.EXPAND)

        # 按钮区域
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ok_btn = wx.Button(self.panel, wx.ID_OK, label="确定")
        self.cancel_btn = wx.Button(self.panel, wx.ID_CANCEL, label="取消")

        self.ok_btn.Bind(wx.EVT_BUTTON, self.on_ok)
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)

        button_sizer.Add(self.ok_btn, 0, wx.ALL, 5)
        button_sizer.Add(self.cancel_btn, 0, wx.ALL, 5)

        main_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER)

        self.panel.SetSizer(main_sizer)

    def load_config(self):
        """
        从配置文件加载设置
        """
        try:
            # 加载最大页数配置
            max_pages = read_properties_from_config("comment_max_pages")
            if max_pages != "nan":
                self.max_pages_ctrl.SetValue(int(max_pages))

            # 加载子评论配置
            fetch_sub = read_properties_from_config("fetch_sub_comments")
            if fetch_sub != "nan":
                # "true" 对应选择"是"(索引0)，其他情况对应"否"(索引1)
                selection = 0 if fetch_sub.lower() == "true" else 1
                self.sub_comment_choice.SetSelection(selection)
        except Exception as e:
            print(f"加载评论配置时出错: {e}")

    def save_config(self):
        """
        保存设置到配置文件
        """
        try:
            # 保存最大页数配置
            max_pages = str(self.max_pages_ctrl.GetValue())
            update_properties_in_config("comment_max_pages", max_pages)

            # 保存子评论配置
            fetch_sub = "true" if self.sub_comment_choice.GetSelection() == 0 else "false"
            update_properties_in_config("fetch_sub_comments", fetch_sub)
        except Exception as e:
            print(f"保存评论配置时出错: {e}")
            wx.MessageBox(f"保存配置时出错: {e}", "错误", wx.OK | wx.ICON_ERROR)

    def on_ok(self, event):
        self.save_config()
        self.EndModal(wx.ID_OK)

    def on_cancel(self, event):
        self.EndModal(wx.ID_CANCEL)

