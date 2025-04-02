'''
设计思路:
打开软件有一个欢迎页,用于首次打开时显示,两个选项,退出和选择文件夹
选择文件夹后,扫描加载文件夹中的音乐文件路径到列表中,用于切换音乐
如果选择的文件夹没有音乐文件则提示没有文件

有:写入配置文件并指定
无:显示欢迎页,暂时不做了

'''
import io
import os
from PIL import Image, ImageTk

from mutagen.flac import FLAC
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3
from PIL.Image import Resampling

# file_path = r"Z:\Music\邹然 - 不再见.mp3"
file_path = r"Z:\Music"
# file_path = r"Z:\Music\李宇春 - 蜀绣.flac"
# file_path = r"Z:\Music\子衿 - 青玉恋.flac"


audio = None
title = None  # 歌名
album = None  # 专辑
artist = None  # 歌手
album_art = None  # 专辑封面
FIXED_SIZE = 100


def music_info(music_path):
    """
    :param music_path:
    :return: 歌名,专辑,歌手,歌词,专辑封面,封面进行处理为100*100

    没做异常处理
    """
    ext = os.path.splitext(music_path)[1].lower()
    if ext == ".flac":
        music_ob = FLAC(music_path)

        tags = music_ob.tags
        return (
            tags.get('TITLE',['Unknown'])[0],
            tags.get('ALBUM',['Unknown'])[0],
            tags.get('ARTIST',['Unknown'])[0],
            tags.get('LYRICS',[''])[0]
        )
    elif ext == ".mp3":
        music_ob = EasyID3(music_path)
        temp_audio = ID3(music_path)
        return music_ob['title'][0], music_ob['album'][0], music_ob['artist'][0], temp_audio.getall("USLT")[0].text
    else:
        print("文件不支持格式,仅支持flac和mp3.")

files = [os.path.join(file_path, f) for f in os.listdir(file_path) if os.path.isfile(os.path.join(file_path, f)) and f.lower().endswith(('.flac', '.mp3'))]
print(len(files))




def parse_lrc_to_dict(lrc_str):
    """
    将LRC格式的歌词字符串转换成字典。
    字典的键是时间（秒），值是对应的歌词文本。
    """
    lrc_dict = {}
    lines = lrc_str.splitlines()

    for line in lines:
        parts = line.split(']')
        lyrics = parts[-1]  # 最后一部分是歌词
        times = parts[:-1]  # 前面的部分都是时间戳

        for time_str in times:
            if '[' in time_str:  # 确保有时间信息
                time_str = time_str.replace('[', '')
                try:
                    # 解析分钟和秒钟
                    m, s = map(float, time_str.split(':'))
                    time_in_seconds = m * 60 + s
                    lrc_dict[time_in_seconds] = lyrics
                except ValueError:
                    print(f"无法解析的时间格式：{time_str}")

    return lrc_dict


# # 示例歌词
# lrc_content = '''[00:00.00]作曲 : RYO ASKA'''
#
# # 解析歌词
# lyrics_dict = parse_lrc_to_dict(lrc_content)
#
# # 获取当前播放时间（例如从音频播放器获取）
# current_time = 0  # 假设当前时间为0秒
#
# # 查找对应时间的歌词
# for time_stamp in sorted(lyrics_dict.keys()):
#     if current_time >= time_stamp:
#         current_lyric = lyrics_dict[time_stamp]
#     else:
#         break
#
# print(current_lyric)  # 输出应显示的歌词

maxlen = 0

# for file in files:
a,b,c,d = music_info(files[200])
print(d)
print()
lyrics_dict = parse_lrc_to_dict(d)

for k, v in lyrics_dict.items():
    print(f"{k}:{v}", len(v))
    # break



