import sounddevice as sd
import soundfile as sf
import numpy as np
import time

# 配置参数
AUDIO_FILE = r"Z:\Music\周杰伦 - 红尘客栈.flac"  # 替换为你的音频文件路径（WAV/FLAC格式）
DEVICE_ID = None  # 默认设备，可通过 sd.query_devices() 查看

data, samplerate = sf.read(AUDIO_FILE, dtype='float32')

# 播放控制
current_frame = 0
is_playing = False
stream = None

def audio_callback(outdata, frames, time, status): # 参数完整
    global current_frame

    if is_playing:
        available_frames = len(data) - current_frame
        if available_frames == 0:
            outdata.fill(0)
            return
        frames_to_read = min(frames, available_frames)
        outdata[:frames_to_read] = data[current_frame:current_frame + frames_to_read]
        current_frame += frames_to_read
        if frames_to_read < frames:
            outdata[frames_to_read:].fill(0)
    else:
        outdata.fill(0)

def toggle_play():
    global is_playing, stream
    is_playing = not is_playing
    if is_playing and stream is None:
        stream = sd.OutputStream(
            samplerate=samplerate,
            device=DEVICE_ID,
            channels=data.shape[1],
            callback=audio_callback,
            dtype='float32'
        )
        stream.start()
    print("状态:", "播放中" if is_playing else "已暂停")

def seek(seconds):
    global current_frame
    current_frame = int(seconds * samplerate)
    print(f"跳转到 {seconds} 秒")

# 测试控制
toggle_play()  # 开始播放
time.sleep(2)  # 播放2秒
seek(10)       # 跳转到10秒
time.sleep(3)  # 继续播放3秒
toggle_play()  # 暂停暂停
time.sleep(3)  # 继续播放3秒
toggle_play()  # 暂停暂停

# 保持程序运行（实际使用时替换为GUI主循环）
input("按回车键退出...")
if stream:
    stream.close()