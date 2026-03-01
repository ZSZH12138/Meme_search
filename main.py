import sys
import io

# 解决 transformers 在 --windowed 模式下 sys.stdout 为 None 的 Bug
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()


import keyboard
import pyperclip
import tkinter as tk
from data_search.RAG import get_ans
from PIL import Image
import win32clipboard
from io import BytesIO
import threading
import winsound
import os


def get_resource_path(relative_path):
    """ 获取资源绝对路径，兼容开发环境和 PyInstaller 环境 """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的路径 (dist/meme_search/_internal)
        base_path = sys._MEIPASS
    else:
        # 开发环境路径
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def show_tip(message):
    tip = tk.Tk()

    # 基础设置
    tip.overrideredirect(True)
    tip.attributes("-topmost", True)
    tip.attributes("-alpha", 0.94)  # 稍微调高一点透明度，确保文字清晰

    # 颜色配置
    bg_color = "#2B2B2B"
    border_color = "#454545"
    text_color = "#FFFFFF"

    # 使用 Frame 模拟边框
    border_frame = tk.Frame(tip, bg=border_color, padx=1, pady=1)
    border_frame.pack()

    content_frame = tk.Frame(border_frame, bg=bg_color)
    content_frame.pack()

    label = tk.Label(
        content_frame,
        text=message,
        bg=bg_color,
        fg=text_color,
        # --- 修复点：移除了 "medium"，使用标准的字体声明 ---
        font=("Microsoft YaHei UI", 10),
        padx=20,
        pady=12
    )
    label.pack()

    # 自动计算宽高
    tip.update_idletasks()
    width = tip.winfo_width()
    height = tip.winfo_height()

    screen_width = tip.winfo_screenwidth()
    screen_height = tip.winfo_screenheight()

    # 距离右下角的边距
    x = screen_width - width - 30
    y = screen_height - height - 60

    tip.geometry(f"+{x}+{y}")

    # 1.5秒后销毁
    tip.after(1500, tip.destroy)
    tip.mainloop()

def copy_image_to_clipboard(image_path):
    image = Image.open(image_path)

    output = BytesIO()
    image.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]
    output.close()

    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()

def on_select(image_path, root):
    copy_image_to_clipboard(image_path)
    winsound.MessageBeep(winsound.MB_ICONASTERISK)
    threading.Thread(
        target=show_tip,
        args=("图片已粘贴至粘贴板",),
        daemon=True
    ).start()
    root.destroy()


def show_popup(texts, links):
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)

    # --- 颜色与样式配置 ---
    BG_COLOR = "#252526"  # 主背景色
    BTN_COLOR = "#333333"  # 按钮颜色
    HOVER_COLOR = "#444444"  # 悬停颜色
    TEXT_COLOR = "#CCCCCC"  # 文字颜色
    ACCENT_COLOR = "#007ACC"  # 强调色（如左侧小装饰）
    CLOSE_HOVER = "#E81123"  # 关闭按钮悬停色

    # 计算窗口位置
    window_width = 450
    # 根据按钮数量动态计算高度，每个按钮约 45px，加上顶部标题栏 30px
    window_height = len(texts) * 50 + 40

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)

    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.configure(bg=BG_COLOR, highlightthickness=1, highlightbackground="#444444")

    # --- 1. 简易标题栏 (方便区分和关闭) ---
    title_bar = tk.Frame(root, bg=BG_COLOR, height=30)
    title_bar.pack(fill="x", side="top")

    title_label = tk.Label(title_bar, text="请选择匹配结果", bg=BG_COLOR, fg="#888888", font=("Microsoft YaHei", 9))
    title_label.pack(side="left", padx=15)

    close_btn = tk.Button(
        title_bar, text="✕", bg=BG_COLOR, fg="#888888", bd=0,
        font=("Microsoft YaHei", 10), cursor="hand2",
        activebackground=CLOSE_HOVER, activeforeground="white",
        command=root.destroy
    )
    close_btn.pack(side="right", ipadx=10, fill="y")

    # --- 2. 按钮美化逻辑 ---
    def on_enter(e):
        e.widget.config(bg=HOVER_COLOR, fg="white")

    def on_leave(e):
        e.widget.config(bg=BTN_COLOR, fg=TEXT_COLOR)

    # --- 3. 渲染按钮列表 ---
    for text, link in zip(texts, links):
        btn_frame = tk.Frame(root, bg=BG_COLOR)
        btn_frame.pack(fill="x", padx=15, pady=4)

        # 按钮左侧的装饰线条（增加设计感）
        accent_bar = tk.Frame(btn_frame, bg=ACCENT_COLOR, width=3)
        accent_bar.pack(side="left", fill="y")

        btn = tk.Button(
            btn_frame,
            text=f"  {text}",  # 加点空格作为左间距
            anchor="w",  # 文字左对齐
            font=("Microsoft YaHei", 10),
            bg=BTN_COLOR,
            fg=TEXT_COLOR,
            bd=0,
            height=2,
            cursor="hand2",
            activebackground=HOVER_COLOR,
            activeforeground="white",
            command=lambda path=get_resource_path(link): on_select(path, root)
        )
        btn.pack(side="left", fill="x", expand=True)

        # 绑定悬停事件
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    root.mainloop()

def on_hotkey():
    query = pyperclip.paste()

    if not query.strip():
        winsound.MessageBeep(winsound.MB_ICONASTERISK)
        threading.Thread(
            target=show_tip,
            args=("粘贴板上无文本",),
            daemon=True
        ).start()
        return
    else:
        winsound.MessageBeep(winsound.MB_ICONASTERISK)
        threading.Thread(
            target=show_tip,
            args=(f"已获取文本：\n{query}",),
            daemon=True
        ).start()

    text, link = get_ans(query)

    # 开新线程显示弹窗
    threading.Thread(target=show_popup, args=(text, link), daemon=True).start()

def quit_program():
    """ 安全退出程序 """
    print("程序正在退出...")
    # 使用 os._exit(0) 可以强制结束所有守护线程并退出
    os._exit(0)

if __name__=="__main__":
    winsound.MessageBeep(winsound.MB_ICONASTERISK)
    threading.Thread(
        target=show_tip,
        args=(f"程序已准备完成",),
        daemon=True
    ).start()
    keyboard.add_hotkey("ctrl+shift+e", on_hotkey)
    keyboard.add_hotkey("ctrl+shift+q", quit_program)
    keyboard.wait()