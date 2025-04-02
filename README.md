# mango-player



心血来潮、闲来无事花了一整天用Python的tkinter写一个简单的本地音乐播放器！

Beause of no job, no offer, can only stay in the school room to writer some shit mountain code to pass the time.



<img src=".\播放界面.png" style="zoom: 80%;" />

**功能**

- 播放，暂停，仅仅支持`mp3`和`flac`文件
- 上一曲、下一曲
- 随机播放、顺序播放、单曲循环
- 展示歌曲名称、歌手名称（专辑名称可以自己在代码里面添加）
- 启动淡入、退出淡出
- 配置文件`mango.conf`记录上次播放的歌曲，上次关闭时窗口位置，方便下次启动记住

> 没有做歌词相关的工作，主要是空间位置不太够，歌词有点太长，另外暂时懒得写了，个人使用够用了

**不足**

- 就一个`main.py`文件，一个界面，代码300行左右，没有复杂的功能，功能之类的没有解耦
- 由于仅打算个人使用，文件信息读取之类的没有做异常处理，默认了我的文件都没问题，都有封面、歌手等信息
- 没有做单例的设计，多次运行就多个窗口
- 音频输出设备切换没有做到，不支持耳机等扬声器热插拔，自己边开发边写边测试，尝试修改未果（无奈）  

**Tips**

- 如果只是想使用该播放器，按照以下目录结构保存必要文件即可，并编辑`mango.conf`文件修改`file_path`字段为你的音乐文件夹

```markdown
mango-player/
├── assets/
│   ├── artist.png
│   └── ...
│   └── random.png
├── mango.conf
└── mango.exe
```

**歌曲**

- **网上下载的资源到本地，使用MusicTag v1.0.9.0进行编辑，批量修改音乐标签，并嵌入歌词和封面到文件中，不然用不了**