# snhlivedownloader

下载live.snh48.com储存的历史视频/Download archived video on live.snh48.com

![example](source/example.gif)

## 功能/Feature

    + 最新：新增全站标题关键词筛选/New: Search video by keywords
    
    + 可选择单个视频或爬取所有视频/ Single Video Mode or Full Download
    + 添加手动合并ts文件功能 / merge downloaded ts
    + 从已存在项目中自动选择断点续传/choose from existing downloads to continue
    + 重新下载已存在项目/re-download existing video (WILL CLEAR OLD FILES!)
    
    + 支持断点续传/ Download from where you left
    + 可选取清晰度/ Choose resolution (if provided by source)
    + 可输出m3u8片段列表(需要简单修改参数)/ .m3u8 file export supported(just change M3U8 variable)

## 使用方法(Linux/Windows)/ Usage:     

    + python >= --version 3.0
    + required modules: lxml, requests

+ 直接使用python代码/Use python script

`python3 snhlivedownloader.py`

+ 使用可执行文件`/dist/snhlivedownloader(Linux)`或`/dist/snhlivedownloader.exe(Windows)`/Use executable

  请把可执行文件和`logging.json`放在同一文件夹下运行

## 关于直播下载/Streaming not supported
> python对于直播流下载功能支持并不好，并且使用python内建库下载直播文件分段、检查可用都有问题，所以就不在此实现。直播流下载储存推荐使用vlc或者ffmpeg(强留推荐，自动分块)或其他软件进行下载。
> Python does not have a good library for streaming download. It is inefficient to use python for streaming watch/download. I recommend use VLC or ffmpeg directly to capture streaming.


## Future works
+ Add GUI with nodejs and HTML/css
+ Change into a more systematic design (separate function files and logging systems)

## 参考/ Reference
    + https://github.com/ShizukuIchi/avgle-downloader/
    + https://pypi.python.org/pypi/m3u8
    + https://github.com/huzhenjie/m3u8_downloader
    + https://gist.github.com/vladignatyev/

### 关于视频版权/About video copyright
视频所有版权为上海丝芭文化传媒集团有限公司所有，本代码仅作为学习使用。请遵守版权所有方所有规定和相关版权法律法规。

All video copyrights are owned by Shanghai Star48 culture media group co.LTD. The script is only for learning purpose. Please comply with Star48's regulation and all relevant Chinese Copyright Laws.

&nbsp;

### 版权/Copyright: [MIT License](https://opensource.org/licenses/MIT)
