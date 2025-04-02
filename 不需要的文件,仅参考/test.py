"""淡入效果演示"""


import tkinter as tk
import time


def fade_in(window, duration=0.5):
    alpha = 0.0
    window.attributes('-alpha', alpha)
    steps = 20
    delay = duration / steps

    for _ in range(steps):
        alpha += 1.0 / steps
        window.attributes('-alpha', alpha)
        window.update()
        time.sleep(delay)


root = tk.Tk()
root.geometry("300x200")
tk.Label(root, text="淡入效果演示", font=('Arial', 16)).pack(pady=50)

# 初始完全透明
root.attributes('-alpha', 0.0)

# 显示窗口后开始淡入
root.after(100, lambda: fade_in(root, 1.0))

root.mainloop()