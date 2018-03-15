''' Defines single functions to perform menu tasks
'''
import logging
import os
import shutil
from __utilities__ import setup_working_path
from __utilities__ import press_to_exit
from __utilities__ import list_directory
from __variables__ import DOMAIN

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

    if DOWNLOAD:
        r = _download_one_video(uri, resolution, working_path)
        if r == 0:
            logger.info("下载完成 | Download finished")
        else:
            logger.info("下载失败 | Download failed")
        return r

    elif M3U8:
        from __HTTPrequests__ import _uri_to_video
        video = _uri_to_video(uri)
        if video:
            video.set_res(resolution)
            _result_getts = video.get_tslist()
            if _result_getts == -1:
                logger.info("__functions__ >> _download_one_video: 没有可用的m3u8列表，无法下载 | No available m3u8 list, downloading failed")
                return -1
            else:
                _result_writets = video.write_tslist(working_path)
                return _result_writets
        else:
            return -1
    else:
        return 0

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
    urls = [videoInfo['site_url'] for videoInfo in allVideoInfoList if videoInfo]

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
                video.write_tslist(working_path)
        else:
            for video in VideoObjects:
                video.write_tslist(working_path)

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
    from __HTTPrequests__ import _uri_to_video

    logger = logging.getLogger()
    logger.info()

    if REDOWNLOAD:
        logger.info("开始重新下载 | Start re-downloading")
    else:
        logger("开始继续下载 | Start Continuing downloading")

    working_path = setup_working_path()
    menu_list = list_directory(working_path, hidden="tmp")

    _chosen = ""
    while True:
        choice = input("请选择'清晰度'层级,如: gaoqing\n选择文件夹 (选 0 退出):")
        if choice == '0':
            return 0
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

            logger.info("为《%s》找到链接：%s at %s", _chosen.split(os.path.sep)[-2], url, res)
            logger.info("found info《%s》：%s at %s", _chosen.split(os.path.sep)[-2], url, res)
    else:
        logger.info("没找到《%s》info.txt信息文件，请检查已下载部分是否存在" + os.linesep
              , _chosen.split(os.path.sep)[-2])
        logger.info("Fail to find《%s》info.txt，please check" + os.linesep)
        return -1

    # 检查网址正确
    valid_url = False
    for site_url in list(DOMAIN.values()):
        valid_url = valid_url or site_url in url
    if not valid_url:
        logger.info("断点续传: 没找到《%s》有效链接，请手动输入网址\n", _chosen.split(os.path.sep)[-2])
        logger.info("Continue Download, invalid site url input.")
        return -1

    # 检查已下载文件名和远程文件名
    tmp_video = _uri_to_video(url)
    if not tmp_video:
        logger.info("继续下载 | Continue Download >> 解析url失败")
        return -1

    if tmp_video.fname != _chosen.split(os.path.sep)[-2]:
        logger.info("断点续传：已存在视频和远程视频不一致")
        logger.info("------------------  有可能覆盖错误视频")
        logger.info("请检查info.txt中的网址是否指向目标视频")
        logger.info("已存在：%s", _chosen.split(os.path.sep)[-2])
        logger.info("远程文件：%s", tmp_video.fname)
        logger.info("Remote filename does not match existing filename")
        logger.info("返回 | Return to menu")
        return -1

    # 检查临时文件
    tmp_path = _chosen + os.path.sep + "tmp"
    if not os.path.isdir(tmp_path):
        logger.info("%s不包含tmp文件夹, 开始新下载", _chosen.replace(os.getcwd(),''))
        logger.info("/tmp not exist, start new download")
    else:
        tmp_files = [name for name in os.listdir(tmp_path) if os.path.isfile(os.path.join(tmp_path, name))]

        if len([name for name in tmp_files if name.endswith('.ts')]) == 0:
            logger.info("没找到ts临时文件，开始新下载")
            logger.info("No .ts files found in /tmp, start new download")
        else:
            logger.info(_chosen.replace(os.getcwd(),''))
            if REDOWNLOAD:
                logger.info("警告：重新下载《%s》-%s 视频将删除tmp文件夹所有下载片段" % (_chosen.split(os.path.sep)[-2], res))
                logger.info("Warning: REDOWNLOAD selected. .ts files in /tmp will be deleted.")
                choice = input("1.继续 (Continue) 2.退出 (默认) (Exit: Default) ")
                if choice == '1':
                    tmp_files = [os.path.join(tmp_path,name) for name in tmp_files]
                    for _file in tmp_files:
                        try:
                            os.remove(_file)
                        except OSError as e:
                            logger.info(e)
                            return -1
                    logger.info("/tmp文件夹已清空")
                    logger.info("/tmp directory is cleared")
                else:
                    return 0
            else:
                return 0

    # url, res in tmp_video
    tmp_video.set_res(res)
    tmp_video.download(working_path)
    result_ts = tmp_video.get_tslist()

    if result_ts == -1:
        logger.info("__functions__ >> continueDownload: 没有可用的m3u8列表，无法下载 | No available m3u8 list, downloading failed")
        return -1
    else:
        result = tmp_video.download(working_path)
        return result

def downloadM3U8(uri):
    ''' Download M3U8 for a single video
    '''
    result = downloadVideo(uri, DOWNLOAD=False, M3U8=True)
    return result

def showProjects():
    ''' Display existing projects by showing directory
    '''
    logger = logging.getLogger()
    logger.info("")
    working_path = setup_working_path()

    list_directory(working_path)
    choice = input("1. 返回 (Home), 默认 (Default) 2. 退出 (Exit)")
    if choice == '2':
        press_to_exit()

    return 0

def reDownload():
    ''' Redownload existing
    '''
    r = continueDownload(REDOWNLOAD=True)
    return r

def mergeTs():
    ''' Merge existing project' ts files into one single ts file
    '''
    logger = logging.getLogger()
    working_path = setup_working_path()


    logger.info("手动合并ts文件,请选择工作文件夹")
    logger.info("Merging existing .ts files. Please select a target folder")
    menu_list = list_directory(working_path)

    while True:
        choice = input("选择文件夹 (选 0 返回) | Please select (0. Return Home): ")
        if choice == '0': return 0
        elif choice in [str(i) for i in range(1, len(menu_list))]:
            _chosen = menu_list[int(choice)-1]['root']

            if not _chosen.endswith('tmp'):
                    print("错误，目前仅支持合并/tmp文件夹")
                    print("Error, only supporting merge /tmp directories")
                    continue

            empty = '1'
            for fn in os.listdir(_chosen):
                if fn.endswith('.ts'):
                    empty = '0'

            if empty == '1':
                print("警告:文件夹不包含任何.ts文件 -> 重新选择")
                print("Warning: no .ts file in folder -> re-select")
                continue

            logger.info("选择 (selected)：%s", _chosen.replace(os.getcwd(), ''))
            working_path = _chosen
            break

    # 开始合并
    if working_path == '':
        logger.info("路径错误: %s", working_path)
        logger.info("Invalid path, return")
        return -1

    try:
        files = [f for f in os.listdir(working_path) if f.endswith('.ts')]
        tsNames = sorted(files, key=lambda f: int(f.split('.')[0]))
        title = working_path.split(os.path.sep)[-3]
        with open(os.path.sep.join(working_path.split(os.path.sep)[:-1]) + os.path.sep + title + '.ts', 'wb') as f:
            for ts in tsNames:
                with open(working_path + os.path.sep + ts, 'rb') as mergefile:
                    shutil.copyfileobj(mergefile, f)
                # os.remove(ts)
            logger.info('%s merged',title)
    except Exception as e:
        logger.info("__functions__ >> merge_ts()")
        logger.info(e)
        return -1

    return 0
