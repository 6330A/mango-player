import os
import random
import time

from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from PIL import Image, ImageTk
import io
from PIL.Image import Resampling
import configparser
import sounddevice as sd
import soundfile as sf
from mutagen.id3 import ID3, APIC
from tkinter import Button, PhotoImage
import tkinter as tk

CONF_FILE = 'mango.conf'
WIN_WIDTH = 498
WIN_HEIGHT = 128

FIXED_SIZE = 128  # 专辑封面宽高
INFO_HEIGHT = 30  # 歌曲信息高度

# 读取配置文件,包括文件路径,记录的上次的播放列表和窗口位置
config = configparser.ConfigParser()
config.read(CONF_FILE)

FILE_PATH = config['Paths']['file_path']
ICON_PATH = config['Paths']['icon_path']

COORDINATE_X = config['Settings']['coordinate_x']
COORDINATE_Y = config['Settings']['coordinate_y']


class MangoPlayer:
    def __init__(self, root):
        self.root = root
        self.root.geometry(f"{WIN_WIDTH}x{WIN_HEIGHT}+{COORDINATE_X}+{COORDINATE_Y}")

        self.root.configure(bg="#FFFFFF")
        self.root.title("")
        self.root.attributes("-alpha", 0.0)

        self.album_art = tk.Frame(root, width=FIXED_SIZE, height=FIXED_SIZE, bg="gray")
        self.album_art.pack_propagate(False)  # 关键!禁止内部控件改变Frame尺寸
        self.album_art.place(x=0, y=0)  # 单位：像素

        self.root.iconbitmap(os.path.join(ICON_PATH, 'logo.ico'))  # 应用logo

        self.music_logo = PhotoImage(file=(os.path.join(ICON_PATH, 'music.png')))
        self.artist_logo = PhotoImage(file=(os.path.join(ICON_PATH, 'artist.png')))
        self.random_logo = PhotoImage(file=(os.path.join(ICON_PATH, 'random.png')))
        self.cycle_logo = PhotoImage(file=(os.path.join(ICON_PATH, 'cycle.png')))
        self.list_logo = PhotoImage(file=(os.path.join(ICON_PATH, 'list.png')))

        self.button_image_pause = PhotoImage(file=(os.path.join(ICON_PATH, 'play.png')))
        self.button_image_play = PhotoImage(file=(os.path.join(ICON_PATH, 'pause.png')))
        self.button_image_front = PhotoImage(file=(os.path.join(ICON_PATH, 'front.png')))
        self.button_image_back = PhotoImage(file=(os.path.join(ICON_PATH, 'back.png')))

        self.label = tk.Label(self.album_art)
        self.label.pack(fill="both", expand=True)  # 关键!和上面的关键一样不能删除

        self.title_label = tk.Label(
            root,
            text="",
            bg="#FFFFFF",
            fg="black",
            font=("Microsoft YaHei", 16 * -1),
        )

        self.title_label.place(x=163, y=6)  # 精确坐标

        self.artist_label = tk.Label(
            root,
            text="",
            bg="#FFFFFF",
            fg="black",
            font=("Microsoft YaHei", 16 * -1),
        )
        self.artist_label.place(x=163, y=34)  # 精确坐标

        self.logo1 = Button(
            image=self.music_logo,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.play_music(),
            # relief="flat",
            bg="white",
            activebackground="white"
        )

        self.logo1.place(
            x=140,
            y=12,
            width=16,
            height=16,
        )

        self.logo2 = Button(
            image=self.artist_logo,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.play_music(),
            relief="flat",
            bg="white",
            activebackground="white"
        )

        self.logo2.place(
            x=140,
            y=40,
            width=16,
            height=16,
        )

        self.logo3 = Button(
            image=self.list_logo,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.change_play_order(),
            relief="flat",
            bg="white",
            activebackground="white"
        )

        self.logo3.place(
            x=140,
            y=69,
            width=16,
            height=16,
        )

        self.button_play = Button(
            image=self.button_image_pause,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.play_music(),
            relief="flat",
            bg="white",
            activebackground="white"
        )

        self.button_play.place(
            x=305,
            y=97,
            width=16,
            height=16,
        )

        self.button_front = Button(
            image=self.button_image_front,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.change_stream(-1, '手动切歌'),
            bg="white",
            activebackground="white"
        )

        self.button_front.place(
            x=140,
            y=99,
            width=23,
            height=14,
        )

        self.button_back = Button(
            image=self.button_image_back,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.change_stream(1, '手动切歌'),
            bg="white",
            activebackground="white"
        )

        self.button_back.place(
            x=464,
            y=99,
            width=23,
            height=14,
        )

        self.files = None  # 歌曲列表
        self.cur_index = None  # 当前歌曲下标
        self.music_count = 0  # 歌曲数量

        self.data = None  # 音频数据
        self.samplerate = None  # 这俩在一起用于播放
        self.stream = None
        self.current_frame = 0
        self.parse = True  # 状态
        self.play_order = 2  # 用于播放控制,切歌是随机还是顺序,3种情况,每次初始化定为2比较好,不能定为0

        self.volume = 0.3  # 设置默认10%音量, 在change_stream这个函数中将data缩小

        self.load_conf_file()  # 加载配置文件

        self.current_device = sd.default.device[1]
        # time.sleep(0.2)  # 模拟耗时操作
        # self.root.deiconify()
        self.root.after(100, lambda: self.fade_in(self.root, 0.3))

        root.protocol('WM_DELETE_WINDOW', self.on_close)

    def fade_in(self, root, duration=0.5):
        alpha = 0.0
        self.root.attributes('-alpha', alpha)
        steps = 10
        delay = duration / steps

        for _ in range(steps):
            alpha += 1.0 / steps
            self.root.attributes('-alpha', alpha)
            self.root.update()
            time.sleep(delay)

    def fade_out(self, root, duration=0.5):
        alpha = 1.0
        self.root.attributes('-alpha', alpha)
        steps = 10
        delay = duration / steps

        for _ in range(steps):
            alpha -= 1.0 / steps
            self.root.attributes('-alpha', alpha)
            self.root.update()
            time.sleep(delay)

        # 比淡入多一行关闭
        self.root.destroy()

    def on_close(self):
        self.current_frame = 0
        if self.stream:  # 消除杂音
            self.stream.stop()

        config['Settings'] = {'cur_index': str(self.cur_index),
                              'coordinate_x': str(self.root.winfo_x()),
                              'coordinate_y': str(self.root.winfo_y())}

        with open(CONF_FILE, 'w') as f:
            config.write(f)
        # 淡出
        self.root.after(100, lambda: self.fade_out(self.root, 0.1))

    def audio_callback(self, outdata, frames, time, status):  # 参数完整
        if not self.parse:
            available_frames = len(self.data) - self.current_frame
            if available_frames == 0:
                outdata.fill(0)
                return
            frames_to_read = min(frames, available_frames)

            outdata[:frames_to_read] = self.data[self.current_frame:self.current_frame + frames_to_read]
            self.current_frame += frames_to_read
            if frames_to_read < frames:
                outdata[frames_to_read:].fill(0)  # 剩余部分静音
                if self.play_order == 1:
                    self.change_stream(0, '自动切歌')  # 此处判断一些是否是单曲模式,是的话传入0即可
                else:
                    self.change_stream(1, '自动切歌')
        else:
            outdata.fill(0)

    def change_play_order(self):
        """
        0: 随机播放
        1: 单曲循环
        2: 顺序播放
        """
        self.play_order = self.play_order + 1
        self.play_order = self.play_order % 3
        print(self.play_order)
        if self.play_order == 0:
            self.logo3.config(image=self.random_logo)
        elif self.play_order == 1:
            self.logo3.config(image=self.cycle_logo)
        else:
            self.logo3.config(image=self.list_logo)

    def play_music(self):
        self.parse = not self.parse
        if self.parse:
            self.button_play.config(image=self.button_image_pause)
        else:
            self.button_play.config(image=self.button_image_play)

        if not self.parse and self.stream is None:
            print(f"[{self.cur_index}]  playing..." + self.files[self.cur_index])
            self.stream = sd.OutputStream(
                samplerate=self.samplerate,
                device=self.current_device,
                channels=self.data.shape[1],
                callback=self.audio_callback,
                dtype='float32'
            )
        self.stream.start()

    def change_stream(self, offset, change_type=""):
        """
        如果是切换上一首和下一首,需要直接播放,切换封面
        :param offset:
        :return:
        """
        if self.stream:  # 消除切歌杂音顺序非常重要,切换歌曲的话第一件事,清空流,然后再加载
            self.stream.stop()

        # 先分为两类,是否随机
        if self.play_order == 0:
            random.seed(int(time.time()))
            self.cur_index = random.randint(0, self.music_count)
        else:
            self.cur_index = (self.cur_index + offset) % self.music_count
        music_path = self.files[self.cur_index]

        self.data, self.samplerate = sf.read(music_path, dtype='float32')  # 神奇,mp3和flac都能直接播放,搞半天也就封面处理了一下,忘了还要处理专辑歌手等信息
        self.data = self.data * self.volume

        if change_type in ['手动切歌', '自动切歌']:
            # 如果是初始化配置也是offset = 0,不播放
            print(change_type)
            self.stream = None
            self.current_frame = 0
            self.parse = True  # 这里有点特殊,play_music会自动取反
            self.play_music()
            self.load_cover(self.files[self.cur_index])  # 切换封面

    def load_conf_file(self):
        """
        配置文件仅仅加载文件目录和上一次听的歌曲index
        然后初始化歌曲数量,加载封面,音频数据加载
        """

        self.files = [os.path.join(FILE_PATH, f) for f in os.listdir(FILE_PATH) if os.path.isfile(os.path.join(FILE_PATH, f)) and f.lower().endswith(('.flac', '.mp3'))]
        self.cur_index = int(config['Settings']['cur_index'])
        self.music_count = len(self.files)

        # 顺带加载封面
        self.load_cover(self.files[self.cur_index])

        # 顺带把音频数据加载初始化
        self.change_stream(0)

        # 统计总数以免用到
        self.music_count = len(self.files)
        # for i, f in enumerate(self.files):
        #     print(f"{i:<4} {f}")
        # print()
        # print(f"总计 {self.music_count} 首歌曲")

    def load_cover(self, music_path):
        """加载并缩放封面图片"""
        if music_path.endswith('.flac'):
            music_ob = FLAC(music_path)
            self.title_label["text"] = music_ob.tags.get('TITLE', ['Unknown'])[0]
            self.artist_label["text"] = music_ob.tags.get('ARTIST', ['Unknown'])[0]
            for pic in music_ob.pictures:
                if pic.type == 3:
                    with Image.open(io.BytesIO(pic.data)) as img:
                        self.process_img(img)
        elif music_path.endswith('.mp3'):
            music_ob = ID3(music_path)  # 可以获取封面和歌词,可见music.py
            music_info = EasyID3(music_path)
            self.title_label["text"] = music_info.get('title', ['Unknown'])[0]
            self.artist_label["text"] = music_info.get('artist', ['Unknown'])[0]
            for tag in music_ob.getall("APIC"):
                if isinstance(tag, APIC):
                    with Image.open(io.BytesIO(tag.data)) as img:
                        self.process_img(img)

    def process_img(self, img):
        img.thumbnail((FIXED_SIZE, FIXED_SIZE), Resampling.LANCZOS)
        self.label.tk_image = ImageTk.PhotoImage(img)
        self.label.config(image=self.label.tk_image)


def main():
    root = tk.Tk()

    player = MangoPlayer(root)
    root.resizable(False, False)
    root.mainloop()


if __name__ == "__main__":
    main()
