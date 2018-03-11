''' Defines single functions to perform menu tasks
'''
import logging
import os
from __utilities__ import setup_working_path
from __utilities__ import press_to_exit

def prompt_resolution():
    ''' Prompt for resolution selection
    '''

    logger = logging.getLogger()

    logger.info("请选择清晰度 | Please select downloading resolution")
    choice = input("1.超清 (chaoqing) 2.高清 (gaoqing) 3.流畅 (liuchang) 0.退出 (Exit)")

    while True:
        if choice == '1':
            choice = 'chaoqing'
            break
        elif choice == '2':
            choice == 'gaoqing'
            break
        elif choice == '3':
            choice == 'liuchang'
            break
        elif choice == '0':
            press_to_exit()
        else:
            continue

    return choice

def _download_one_video(uri, resolution, working_path):
    ''' Wrapper function: download 1 video with resolution and working_path
        return 0 on success, -1 on failure
    '''
    from __HTTPrequests__ import _uri_to_video
    logger = logging.getLogger()

    video = _uri_to_video(uri)
    if video:
        video.set_res(resolution)
        result = video.get_tslist()

        if result == -1:
            logger.info("__functions__ >> _download_one_video: 没有可用的m3u8列表，无法下载 | No available m3u8 list, downloading failed")
            return -1
        else:
            result2 = video.download(working_path)
            return result2
    else:
        return -1

def downloadVideo(uri, DOWNLOAD=True, M3U8=False):
    ''' Download a single video, when DOWNLOAD == False, output video information
    '''
    logger = logging.getLogger()

    logger.info("")
    logger.info("下载视频 | Download Video")
    logger.info("视频地址 | Video url: %s" % uri)

    working_path = setup_working_path()
    resolution = prompt_resolution()

    r = _download_one_video(uri, resolution, working_path)
    if r == 0:
        logger.info("下载完成 | Download finished")
    else:
        logger.info("下载失败 | Download failed")

    return r

def downloadAllVideo(domain, DOWNLOAD=False, M3U8=False):
    ''' Scrape all videos on domain, when DOWNLOAD == True, download them all (this is likely to
            fail after a while because the site will slow down your speed and eventually give you a connection error.)
        You can also download all m3u8 list to text files by setting M3U8 == True
        Return a list of basic video information if no DOWNLOAD or M3U8, return a list of video objects otherwise
    '''
    from __HTTPrequests__ import get_siteVideoList
    from __HTTPrequests__ import _urls_to_videos

    logger = logging.getLogger()
    logger.info("")

    logger.info("采集全部视频信息 | Gathering all video information")
    logger.info("网站地址|on site: %s" % domain)

    working_path = setup_working_path()
    resolution = prompt_resolution()

    allVideoInfoList = get_siteVideoList(domain)[0]
    urls = [videoInfo['site_url'] for videoInfo in allVideoInfoList]

    if DOWNLOAD or M3U8:
        from __HTTPrequests__ import get_batch_M3U8

        VideoObjects = _urls_to_videos(urls) # one pool operation
        results_M3U8 = get_batch_M3U8(VideoObjects, resolution) # another pool operation

        logger.info("")
        logger.info("信息采集完毕 | Information gather.")
        metrics = "%s/%s" % (len([r for r in results_M3U8 if r == 0]), len(results_M3U8))
        logger.info("本次采集到 %s 可下载视频 | total %s downloadable videos." % (metrics, metrics))

        if DOWNLOAD:
            logger.info("开始逐个下载")
            for video in VideoObjects:
                video.download(working_path)

        return VideoObjects
    else:
        logger.info("")
        logger.info("信息采集完毕 | Information gather.")
        logger.info("共%s个视频 | Total %s video on site." % (len(urls), len(urls)))

    return allVideoInfoList

def searchVideo(domain, keyword):
    ''' Search domain for videos with keyword, return a list of matched VideoInfo
        return [] if any error
    '''
    from __HTTPrequests__ import get_siteVideoList
    from __utilities__ import compare_to_search_keywords
    from __variables__ import GREENLET_SIZE

    logger = logging.getLogger()
    logger.info("")
    logger.info("采集全部视频信息 | Gathering all video information")
    logger.info("网站地址|on site: %s" % domain)

    allVideoInfoList = get_siteVideoList(domain)[0]

    if not allVideoInfoList:
        logger.info("searchVideo: 没找到任何视频 | No video found on site")
        return []

    def search_wrapper(VideoInfo, keyword):
        ''' VideoInfo {info} + keyword >> {info} if found, else {empty}
        '''
        if compare_to_search_keywords(VideoInfo['fname'], keyword):
            return VideoInfo
        else:
            return {}

    import gevent.pool as pool
    p = pool.Pool(GREENLET_SIZE)
    results = map(search_wrapper, zip(allVideoInfoList, [keyword] * len(allVideoInfoList)))
    p.join()

    return results

def continueDownload(REDOWNLOAD=False):
    ''' Continue your previous download, when REDOWNLOAD == True, erase original copies
    '''
    logger = logging.getLogger()
    logger.info(__name__)
global LOGGER
    menu_list = list_directory(path, hidden="tmp")

    _chosen = ""
    while True:
        choice = input("请选择'清晰度'层级,如: gaoqing\n选择文件夹 (选 0 退出):")
        if choice == '0':
            MyExit()
        elif choice in [str(i) for i in range(1, len(menu_list))]:
            _chosen = menu_list[int(choice)-1]['root']
            break

    # 检查信息文件
    info_file = _chosen + os.path.sep + "info.txt"
    url = ""
    res = ""
    if os.path.isfile(info_file):
        with open(info_file, 'r') as f:
            for line in f.readlines():
                if "video_url" in line:
                    url = line.split(": ")[1].strip()
                if "resolution" in line:
                    res = line.split(": ")[1].strip()

            LOGGER.info("为《%s》找到链接：%s at %s", _chosen.split(os.path.sep)[-2], url, res)
    else:
        LOGGER.info("没找到《%s》info.txt信息文件，请检查已下载部分是否存在\n"
              , _chosen.split(os.path.sep)[-2])
        MyExit()

    # 检查网址正确
    valid_url = False
    for site_url in [SNH48LIVE_API,BEJ48LIVE_API,CKG48LIVE_API,GNZ48LIVE_API,SHY48LIVE_API]:
        valid_url = valid_url or site_url in url
    if not valid_url:
        LOGGER.info("断点续传: 没找到《%s》有效链接，请手动输入网址\n", _chosen.split(os.path.sep)[-2])
        MyExit()

    # 检查已下载文件名和远程文件名
    parsed = _get_downloadable_from_url(url, res)
    parsed_fname = parsed['fname']
    if parsed_fname != _chosen.split(os.path.sep)[-2]:
        LOGGER.info("断点续传：已存在视频和远程视频不一致")
        LOGGER.info("------------------  有可能覆盖错误视频")
        LOGGER.info("请检查info.txt中的网址是否指向目标视频")
        LOGGER.info("已存在：%s", _chosen.split(os.path.sep)[-2])
        LOGGER.info("远程文件：%s", parsed_fname)
        print("返回")
        MyExit()

    # 检查临时文件
    tmp_path = _chosen + os.path.sep + "tmp"
    if not os.path.isdir(tmp_path):
        LOGGER.info("%s不包含tmp文件夹, 开始新下载", _chosen.replace(os.getcwd(),''))
    else:
        tmp_files = [name for name in os.listdir(tmp_path) if os.path.isfile(os.path.join(tmp_path, name))]

        if len([name for name in tmp_files if name.endswith('.ts')]) == 0:
            LOGGER.info("没找到ts临时文件，开始新下载\n")
        else:
            LOGGER.info(_chosen.replace(os.getcwd(),''))
            if REDOWNLOAD:
                choice = input("警告：重新下载《%s》-%s 视频将删除tmp文件夹所有下载片段\n1.继续 2.退出(默认) "
                            % (_chosen.split(os.path.sep)[-2], res))
                if choice == '1':
                    tmp_files = [os.path.join(tmp_path,name) for name in tmp_files]
                    for _file in tmp_files:
                        try:
                            os.remove(_file)
                        except OSError as e:
                            LOGGER.info(e)
                            press_to_exit()
                    LOGGER.info("tmp文件夹已清空")
                else:
                    MyExit()

    return [url, res]


    return

def downloadM3U8(uri):
    ''' Download M3U8 for a single video
    '''
    logger = logging.getLogger()
    downloadVideo(uri, DOWNLOAD=False, M3U8=False)
    logger.info(__name__)
    return

def showProjects():
    ''' Display existing projects by showing directory
    '''
    logger = logging.getLogger()
    logger.info(__name__)
    input("1. 返回 2. 退出")
    return

def reDownload():
    ''' Redownload existing
    '''
    logger = logging.getLogger()
    logger.info(__name__)
    continueDownload(REDOWNLOAD=True)
    return

def mergeTs():
    ''' Merge existing project' ts files into one single ts file
    '''
    logger = logging.getLogger()
    logger.info(__name__)
    return
