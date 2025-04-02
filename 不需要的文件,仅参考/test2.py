"""单例,也没完成"""

import tkinter as tk
import socket


def is_single_instance():
    try:
        # 创建一个 TCP 套接字
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 尝试绑定到本地地址和端口
        server.bind(('127.0.0.1', 9999))
        # 开始监听
        server.listen(1)
        return True
    except socket.error:
        return False


if __name__ == "__main__":
    if is_single_instance():
        root = tk.Tk()
        root.title("单实例 Tkinter 应用")
        label = tk.Label(root, text="这是单实例应用")
        label.pack(pady=20)
        root.mainloop()
    else:
        print("已有实例正在运行，无法再次启动。")