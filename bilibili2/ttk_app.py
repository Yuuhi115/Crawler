import tkinter as tk
import ttkbootstrap as ttk
from click import style
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox, Querybox
import threading
import os
import sys
import pandas as pd
from wx.lib.sized_controls import border

from fetch_site import *
from fetch_video import run_video_crawler
from utils import *
from proxy_config_dialog import ProxyConfigDialog
from export_config_dialog import ExportConfigDialog
from choice_dialog import ChoiceDialog


class BilibiliCrawlerFrame(ttk.Window):
    def __init__(self):
        super().__init__(title="Bilibili视频下载器", minsize=(600, 600))
        self.batch_download_stop_flag = False
        self.batch_download_status = False
        self.cookie_expiry = None
        self.batch_data = None
        self.batch_file_path = None
        self.create_ui()
        self.center_window()
        self.check_cookies_status()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

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
        style = ttk.Style()
        style.theme_use("superhero")
        # 创建半透明灰色背景、白色字体的按钮样式
        style.configure(
            "SemiTransparent.TButton",
            background="gray",      # 背景色
            foreground="white",     # 字体颜色
            bordercolor="gray",     # 边框颜色
            borderwidth=0,          # 边框宽度
            relief="raised",        # 添加这项
            lightcolor="gray",      # 高亮颜色
            darkcolor="gray",
            padding=(40, 7),  # 调整这个值来控制高度 (水平, 垂直)
        )

        # 配置鼠标悬停效果
        style.map(
            "SemiTransparent.TButton",
            background=[("active", "lightgray")],  # 悬停时的背景色
            foreground=[("active", "white")],  # 悬停时的字体颜色
            bordercolor = [("active", "lightgray")]  # 悬停时的边框颜色
        )
        # 创建主框架
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=YES, padx=10, pady=10)

        # 登录区域
        login_frame = ttk.LabelFrame(main_frame, text="登录设置", padding=10)
        login_frame.pack(fill="x", pady=(0, 10))

        self.login_btn = ttk.Button(login_frame, text="扫码登录并保存Cookies", bootstyle="primary", command=self.on_login)
        self.login_btn.pack(fill="x", pady=(0, 5))

        self.cookies_status = ttk.Label(login_frame, text="Cookies状态: 未检测到")
        self.cookies_status.pack(anchor="w")

        # 其他功能区域
        other_frame = ttk.LabelFrame(main_frame, text="其他功能", padding=10)
        other_frame.pack(fill="x", pady=(0, 10))

        # 功能按钮行1
        btn_frame1 = ttk.Frame(other_frame)
        btn_frame1.pack(fill="x", pady=(0, 5))

        self.search_btn = ttk.Button(btn_frame1, text="搜索视频", command=self.on_search, width=13)
        self.search_btn.pack(side="left", padx=(0, 5))

        self.uploader_btn = ttk.Button(btn_frame1, text="获取up主页面", command=self.on_open_uploader, width=13)
        self.uploader_btn.pack(side="left", padx=(0, 5))

        self.favorite_btn = ttk.Button(btn_frame1, text="检索收藏夹", command=self.on_open_favorite, width=13)
        self.favorite_btn.pack(side="left", padx=(0, 5))

        self.rotate_video_btn = ttk.Button(btn_frame1, text="视频翻转", command=self.on_rotate_video, width=13)
        self.rotate_video_btn.pack(side="left", padx=(0, 5))

        self.check_update_btn = ttk.Button(btn_frame1, text="检查更新", command=self.on_check_update, width=13)
        self.check_update_btn.pack(side="left", padx=(0, 5))

        # # 功能按钮行2
        # btn_frame2 = ttk.Frame(other_frame)
        # btn_frame2.pack(fill="x", pady=(0, 5))

        # 配置按钮行
        config_frame = ttk.LabelFrame(other_frame, text="配置区域", padding=10)
        config_frame.pack(fill="x", pady=(0, 5))

        self.export_config_btn = ttk.Button(config_frame, text="导出设置", command=self.on_config, width=13)
        self.export_config_btn.pack(side="left", padx=(0, 5))

        self.proxy_config_btn = ttk.Button(config_frame, text="代理设置", command=self.on_proxy_config, width=13)
        self.proxy_config_btn.pack(side="left", padx=(0, 5))

        # 视频下载区域
        video_frame = ttk.LabelFrame(main_frame, text="视频下载", padding=10)
        video_frame.pack(fill="x", pady=(0, 10))

        # 单个视频下载
        url_frame = ttk.Frame(video_frame)
        url_frame.pack(fill="x", pady=(0, 5))

        ttk.Label(url_frame, text="视频链接:").pack(side="left")
        self.url_text = ttk.Entry(url_frame)
        self.url_text.pack(side="left", fill="x", expand=YES, padx=(5, 5))
        self.download_btn = ttk.Button(url_frame, text="下载", command=self.on_download, width=10, bootstyle="success")
        self.download_btn.pack(side="left")

        # 批量下载
        batch_frame = ttk.Frame(video_frame)
        batch_frame.pack(fill="x")

        self.import_batch_btn = ttk.Button(batch_frame, text="导入视频列表", command=self.on_import_batch)
        self.import_batch_btn.pack(side="left", padx=(0, 5))

        self.imported_file_label = ttk.Label(batch_frame, text="未选择文件")
        self.imported_file_label.pack(side="left", fill="x", expand=YES)

        self.stop_btn = ttk.Button(batch_frame, text="终止批量下载", command=self.on_stop_batch,
                                   bootstyle="danger", state=DISABLED)
        self.stop_btn.pack(side="left", padx=(0,5))

        self.batch_download_btn = ttk.Button(batch_frame, text="批量下载", state=DISABLED,
                                             command=self.on_batch_download, bootstyle="success",
                                             width=10)
        self.batch_download_btn.pack(side="left")


        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="运行日志", padding=5)
        log_frame.pack(fill="both", expand=YES, pady=(0, 10))

        log_text_frame = ttk.Frame(log_frame)
        log_text_frame.pack(fill="both", expand=YES)

        self.log_text = ttk.Text(log_text_frame, height=10, wrap="none")
        v_scroll = ttk.Scrollbar(log_text_frame, orient="vertical", command=self.log_text.yview)
        # h_scroll = ttk.Scrollbar(log_text_frame, orient="horizontal", command=self.log_text.xview)
        self.log_text.configure(yscrollcommand=v_scroll.set)

        self.log_text.pack(side="left", fill="both", expand=YES)
        v_scroll.pack(side="right", fill="y")
        # h_scroll.pack(side="bottom", fill="x")

        # 重定向标准输出到文本框
        sys.stdout = LogTarget(self.log_text)
        sys.stderr = LogTarget(self.log_text, isError=True)

        # 底部按钮
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill="x")

        self.clear_btn = ttk.Button(bottom_frame, text="清空日志", command=self.on_clear_log)
        self.clear_btn.pack(side="left", padx=(0, 5))

        self.exit_btn = ttk.Button(bottom_frame, text="退出", command=self.on_exit, bootstyle="danger", width=10)
        self.exit_btn.pack(side="right")

    def check_cookies_status(self):
        """
        检查cookies状态并更新UI显示
        """
        try:
            if os.path.exists(resource_path("./app_config/cookies.json")):
                self.cookie_expiry = self.get_cookie_expiry("SESSDATA")
                if self.cookie_expiry is not None:
                    if self.cookie_expiry > 0:
                        self.cookies_status.configure(
                            text=f"Cookies状态: 已检测到 (可下载高清视频), 有效期还剩: {self.cookie_expiry} 天")
                    else:
                        self.cookies_status.configure(text="Cookies状态: 已过期 (需重新登录获取)")
                else:
                    # 如果无法获取过期时间，显示基本状态
                    self.cookies_status.configure(text="Cookies状态: 已检测到 (可下载高清视频)")
            else:
                self.cookies_status.configure(text="Cookies状态: 未检测到 (只能下载低清视频)")
        except Exception as e:
            print(f"Error checking cookies status: {e}")
            # 出错时显示默认信息
            self.cookies_status.configure(text="Cookies状态: 检查出错")

    def on_login(self):
        login_thread = threading.Thread(target=self.login_worker)
        login_thread.daemon = True
        login_thread.start()
        self.check_cookies_status()

    def login_worker(self, account=None, password=None):
        # 执行登录
        try:
            if run_crawler_login(username=account, password=password):
                self.after(0, self.on_login_complete)
            else:
                Messagebox.show_warning("登录失败", "提示")
        except Exception as e:
            Messagebox.show_error(f"登录过程中出现错误: {str(e)}", "错误")

    def on_login_complete(self):
        self.check_cookies_status()
        Messagebox.show_info("登录成功，Cookies已保存", "提示")

    def on_search(self):
        keyword = Querybox.get_string("请输入搜索关键词:", "视频搜索")
        if keyword:
            search_thread = threading.Thread(target=self.search_worker, args=(keyword,))
            search_thread.daemon = True
            search_thread.start()
        else:
            Messagebox.show_warning("请输入搜索关键词", "提示")

    def on_config(self):
        dialog = ExportConfigDialog(self)
        dialog.show()

    def on_proxy_config(self):
        dialog = ProxyConfigDialog(self)
        dialog.show()

    def on_open_uploader(self):
        uid = Querybox.get_string("请输入up主id:", "uid:")
        if uid:
            search_space_thread = threading.Thread(target=self.search_space_worker, args=(uid,))
            search_space_thread.daemon = True
            search_space_thread.start()
        else:
            Messagebox.show_warning("请输入输入up主id", "提示")

    def search_space_worker(self, uid):
        try:
            run_uploader_page(uid)
        except Exception as e:
            Messagebox.show_error(f"搜索过程中出现错误: {str(e)}", "错误")

    def on_open_favorite(self):
        if os.path.exists(resource_path("./app_config/cookies.json")):
            uid = get_cookie_by_name("DedeUserID").get("value")
            fav_category_list = self.search_favorite_category(uid)
            if fav_category_list:
                # 创建收藏夹选项列表
                choices = [f"{fav['title']}" for fav in fav_category_list]
                # 使用自定义的 ChoiceDialog 替代不存在的 Querybox.get Choice
                dialog = ChoiceDialog(self, "收藏夹选择", "请选择收藏夹:", choices)
                selected = dialog.show()

                if selected and selected != "取消":
                    # 找到选中的收藏夹
                    selected_favorite = None
                    for fav in fav_category_list:
                        if fav['title'] == selected:
                            selected_favorite = fav
                            break

                    if selected_favorite:
                        print(f"已选择收藏夹: {selected_favorite['title']} (ID: {selected_favorite['id']})")
                        # 在后台线程中执行搜索操作
                        search_favorite_thread = threading.Thread(
                            target=self.search_favorite_worker,
                            args=(selected_favorite, uid)
                        )
                        search_favorite_thread.daemon = True
                        search_favorite_thread.start()
                else:
                    print("未选择收藏夹")
        else:
            Messagebox.show_warning("请先登录！", "提示")

    def search_favorite_category(self, uid):
        try:
            fav_category_list = run_favorite_category(uid)
            if fav_category_list is not None:
                return fav_category_list
        except Exception as e:
            Messagebox.show_error(f"搜索收藏夹列表过程中出现错误: {str(e)}", "错误")

    def search_favorite_worker(self, selected_favorite, uid):
        try:
            run_favorite_category_page(uid, selected_favorite['id'], selected_favorite['title'])
        except Exception as e:
            Messagebox.show_error(f"检索收藏夹'{selected_favorite['title']}'信息过程中出现错误: {str(e)}", "错误")

    def search_worker(self, key_word):
        try:
            run_search_page(key_word)
        except Exception as e:
            Messagebox.show_error(f"搜索过程中出现错误: {str(e)}", "错误")

    def on_download(self):
        url = self.url_text.get()
        if not url:
            Messagebox.show_warning("请输入视频链接", "提示")
            return

        # 检查URL是否包含bilibili视频链接特征
        if not ("www.bilibili.com/video/BV" in url or "www.bilibili.com/bangumi/play/ep" in url):
            Messagebox.show_warning("请输入有效的Bilibili视频链接", "提示")
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
            self.after(0, lambda: Messagebox.show_info("视频下载完成", "提示"))
        except Exception as e:
            self.after(0, lambda: Messagebox.show_error(f"下载过程中出现错误: {str(e)}", "错误"))

    def on_import_batch(self):
        """
        导入视频列表按钮事件处理
        """
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="选择视频列表文件",
            filetypes=[
                ("Excel文件", "*.xlsx"),
                ("CSV文件", "*.csv"),
                ("所有文件", "*.*")
            ]
        )

        if file_path:
            self.import_batch_worker(file_path)

    def import_batch_worker(self, file_path):
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
                Messagebox.show_error("不支持的文件格式，请选择.xlsx或.csv文件", "错误")
                return

            # 检查必要的列是否存在
            if 'link' not in df.columns:
                Messagebox.show_error("文件中缺少'link'列，请确保文件包含视频链接", "错误")
                return

            # 检查title列是否存在
            has_title = 'title' in df.columns
            has_download_status = 'download_status' in df.columns

            # 获取链接列
            links = df['link'].tolist()  # 转换为列表
            select_links = select_df['link'].tolist()

            if not links:
                Messagebox.show_warning("文件中没有找到有效的视频链接", "提示")
                return

            # 保存批量数据
            self.batch_data = select_df
            self.batch_file_path = file_path

            # 更新UI显示
            file_name = os.path.basename(file_path)
            self.imported_file_label.configure(text=f"已导入: {file_name} ({len(links)}个视频)")
            self.batch_download_btn.configure(state=NORMAL)

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

            Messagebox.show_info(f"成功导入 {len(select_links)} 个视频链接, 已下载 {len(exclude_df)} 个", "提示")

        except Exception as e:
            error_msg = f"导入视频列表过程中出现错误: {str(e)}"
            print(error_msg)
            Messagebox.show_error(error_msg, "错误")

    def on_batch_download(self):
        """
        批量下载按钮事件处理
        """
        if self.batch_data is None:
            Messagebox.show_warning("请先导入视频列表文件", "提示")
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
            self.stop_btn.configure(state=NORMAL)


            # 获取链接列
            links = df['link'].dropna().tolist()  # 删除空值并转换为列表

            if not links:
                self.after(0, lambda: Messagebox.show_warning("文件中没有找到有效的视频链接", "提示"))
                return

            print(f"开始批量下载 {len(links)} 个视频...")

            # 逐个下载视频
            success_count = 0
            fail_count = 0

            for i, link in enumerate(links):
                # 检查是否需要终止
                if self.batch_download_stop_flag:
                    print("收到终止请求，停止批量下载...")
                    self.after(0, lambda: Messagebox.show_warning(
                        f"批量下载已终止!\n已完成: {i} 个\n成功: {success_count} 个\n失败: {fail_count} 个",
                        "提示"))
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
                        if(run_video_crawler(link, "video")):
                            success_count += 1
                            # 更新原始DataFrame中的download_status
                            # 找到原始DataFrame中对应链接的行索引并更新状态
                            original_index = original_df[original_df['link'] == link].index
                            if not original_index.empty:
                                original_df.loc[original_index[0], 'download_status'] = 1
                        else:
                            fail_count += 1
                    elif "www.bilibili.com/bangumi/play/ep" in link:
                        if(run_video_crawler(link, "anime")):
                            success_count += 1
                            # 更新原始DataFrame中的download_status
                            original_index = original_df[original_df['link'] == link].index
                            if not original_index.empty:
                                original_df.loc[original_index[0], 'download_status'] = 1
                        else:
                            fail_count += 1
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
            self.stop_btn.configure(state=DISABLED)

            # 显示下载结果
            self.after(0, lambda: Messagebox.show_info(
                f"批量下载完成!\n成功: {success_count} 个\n失败: {fail_count} 个",
                "提示"))

            print(f"批量下载完成! 成功: {success_count} 个, 失败: {fail_count} 个")

        except Exception as e:
            # 重置终止标志
            self.batch_download_stop_flag = False
            error_msg = f"批量下载过程中出现错误: {str(e)}"
            print(error_msg)
            self.after(0, lambda: Messagebox.show_error(error_msg, "错误"))

    def on_rotate_video(self):
        """处理视频旋转功能"""
        from tkinter import filedialog
        input_path = filedialog.askopenfilename(
            title="选择要旋转的视频文件",
            filetypes=[
                ("视频文件", "*.mp4"),
                ("所有文件", "*.*")
            ]
        )

        if input_path:
            # 选择旋转角度
            choices = ["90度", "180度", "270度"]
            # 创建自定义对话框来选择角度
            dialog = ChoiceDialog(self, "旋转设置", "请选择旋转角度(顺时针):", choices)
            angle_choice = dialog.show()

            if angle_choice and angle_choice != "取消":
                angles = {"90度": 90, "180度": 180, "270度": 270}
                angle = angles[angle_choice]

                # 选择输出文件路径
                output_path = filedialog.asksaveasfilename(
                    title="保存旋转后的视频",
                    defaultextension=".mp4",
                    filetypes=[("MP4 files", "*.mp4")]
                )

                if output_path:
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

    def rotate_video_worker(self, input_path, output_path, angle):
        """视频旋转工作线程"""
        try:
            print(f"开始旋转视频: {input_path}")
            print(f"旋转角度: {angle}度")

            # 执行视频旋转
            success = rotate_video(input_path, output_path, angle)

            if success:
                self.after(0, lambda: Messagebox.show_info(
                    f"视频旋转完成!\n已保存至: {output_path}",
                    "提示"))
                print(f"视频旋转完成! 已保存至: {output_path}")
            else:
                self.after(0, lambda: Messagebox.show_error("视频旋转失败，请查看日志", "错误"))
        except Exception as e:
            error_msg = f"视频旋转过程中出现错误: {str(e)}"
            print(error_msg)
            self.after(0, lambda: Messagebox.show_error(error_msg, "错误"))

    def on_check_update(self):
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
                update_msg = f"{return_dict['update_message']}\n\n更新内容: \n{update_content}"
                update_url = return_dict["update_url"]
                # 在主线程中显示对话框
                self.after(0, lambda: self.show_update_dialog(update_msg, update_url))
            else:
                self.after(0, lambda: Messagebox.show_info(return_dict['update_message'], "提示"))
        elif return_dict["code"] == 403:
            self.after(0, lambda: Messagebox.show_info("请开启代理后再检测更新", "提示"))
        else:
            self.after(0, lambda: Messagebox.show_error("未知异常，请联系作者", "错误"))

    def show_update_dialog(self, message, url):
        """在主线程中显示更新对话框"""
        result = Messagebox.okcancel(message, "更新提示")
        if result == "OK":
            import webbrowser
            webbrowser.open(url)

    def on_stop_batch(self):
        """
        终止批量下载按钮事件处理
        """
        if hasattr(self,
                   'batch_download_stop_flag') and self.batch_download_stop_flag == False and self.batch_download_status == True:
            self.batch_download_stop_flag = True
            self.batch_download_status = False
            self.stop_btn.config(state=DISABLED)
            print("正在发送终止批量下载请求...")
            Messagebox.show_info("已发送终止请求，正在停止批量下载...", "提示")
        else:
            print("当前没有正在进行的批量下载任务")
            Messagebox.show_info("当前没有正在进行的批量下载任务", "提示")

    def on_clear_log(self):
        self.log_text.delete(1.0, END)

    def on_exit(self):
        self.destroy()


class LogTarget:
    def __init__(self, text_ctrl, isError=False):
        self.text_ctrl = text_ctrl
        self.isError = isError

    def write(self, text):
        self.text_ctrl.insert(END, text)
        self.text_ctrl.see(END)

    def flush(self):
        pass


class BilibiliCrawlerApp:
    def __init__(self):
        self.window = BilibiliCrawlerFrame()

    def run(self):
        self.window.mainloop()


if __name__ == '__main__':
    app = BilibiliCrawlerApp()
    app.run()
