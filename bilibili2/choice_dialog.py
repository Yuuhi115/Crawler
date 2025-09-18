# choice_dialog.py
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class ChoiceDialog:
    """自定义选择对话框"""

    def __init__(self, parent, title, message, choices):
        self.result = None
        self.top = ttk.Toplevel(parent)
        self.top.title(title)
        self.top.geometry("300x300")
        self.top.transient(parent)
        self.top.grab_set()

        # 居中显示
        self.top.update_idletasks()
        x = (self.top.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.top.winfo_screenheight() // 2) - (350 // 2)
        self.top.geometry(f"300x300+{x}+{y}")

        # 创建主框架
        main_frame = ttk.Frame(self.top, padding=20)
        main_frame.pack(fill="both", expand=YES)

        # 消息标签
        ttk.Label(main_frame, text=message).pack(pady=(0, 10))

        # 按钮框架（先创建并放置在底部）
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side="bottom", fill="x", pady=(10, 0))

        # 创建一个内部框架来居中按钮
        button_inner_frame = ttk.Frame(button_frame)
        button_inner_frame.pack(expand=YES)

        # 取消按钮
        ttk.Button(
            button_inner_frame,
            text="取消",
            bootstyle="secondary",
            command=self.on_cancel,
            width=10,  # 设置按钮宽度
        ).pack(side="left", padx=(0, 5))

        # 确定按钮
        ttk.Button(
            button_inner_frame,
            text="确定",
            bootstyle="success",
            command=self.on_ok,
            width=10,  # 设置按钮宽度
        ).pack(side="left", padx=(0, 5))


        # 创建带滚动条的框架来容纳选项（放在按钮之上）
        choice_frame = ttk.Frame(main_frame)
        choice_frame.pack(side="top", fill="both", expand=YES)

        # 创建画布和滚动条
        canvas = ttk.Canvas(choice_frame)
        scrollbar = ttk.Scrollbar(choice_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        # 配置滚动区域
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 选择变量
        self.choice_var = ttk.StringVar()

        # 创建单选按钮
        for choice in choices:
            ttk.Radiobutton(
                scrollable_frame,
                text=choice,
                variable=self.choice_var,
                value=choice
            ).pack(anchor="w", pady=2, fill="x", padx=(0, 10))

        # 默认选择第一个
        if choices:
            self.choice_var.set(choices[0])

        # 布局画布和滚动条
        canvas.pack(side="left", fill="both", expand=YES)
        scrollbar.pack(side="right", fill="y")

        # 绑定鼠标滚轮事件（只对画布生效）
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        # 只在鼠标悬停在画布上时绑定滚轮事件
        canvas.bind("<MouseWheel>", _on_mousewheel)
        canvas.bind("<Enter>", lambda e: canvas.focus_set())

        # 绑定回车键到确定按钮
        self.top.bind('<Return>', lambda e: self.on_ok())
        self.top.bind('<Escape>', lambda e: self.on_cancel())

    def on_ok(self):
        self.result = self.choice_var.get()
        self.top.destroy()

    def on_cancel(self):
        self.result = "取消"
        self.top.destroy()

    def show(self):
        self.top.wait_window()
        return self.result
