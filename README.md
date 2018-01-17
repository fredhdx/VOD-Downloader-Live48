# snhlivedownloader

下载live.snh48.com储存的历史视频/Download archived video on live.snh48.com

## 功能/Feature

    + 支持断点续传/ Download from where you left
    + \[使用\]可选择单个视频或爬取所有视频/ Single Video Mode or Full Download
    + 可选取清晰度/ Choose resolution (if provided by source)
    + 可输出m3u8片段列表(需要简单修改参数)/ .m3u8 file export supported(just change M3U8 variable)
    + 添加手动合并ts文件功能（需要import as module)
    + \[使用\]从已存在项目中自动选择断点续传/choose from existing downloads to continue
    + \[使用\]重新下载已存在项目/re-download existing video (WILL CLEAR OLD FILES!)

## 使用方法(Linux/Windows)/ Usage:     

    + python >= --version 3.0
    + required modules: lxml, requests

 `python3 snh48downloader.py`
   
## 关于直播下载
> python对于直播流下载功能支持并不好，并且使用python内建库下载直播文件分段、检查可用都有问题，所以就不在此实现。直播流下载储存推荐使用vlc或者ffmpeg(强留推荐，自动分块)或其他软件进行下载。


## 等待完善/TO DO:
    - complete error message handling

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
