''' Defines single functions to perform menu tasks
'''
import logging
import os

def downloadVideo(uri, DOWNLOAD=True, M3U8=False):
    ''' Download a single video, when DOWNLOAD == False, output video information
    '''
    from __HTT
    logger = logging.getLogger()
    logger.info("下载视频 | Download Video")
    logger.info("视频地址: %s" % uri)

    video =
    title = ''
    logger.info("%s 下载完成" % title + os.linesep)
    return

def downloadAllVideo(domain, DOWNLOAD=False, M3U8=False):
    ''' Scrape all videos on domain, when DOWNLOAD == True, download them all (this is likely to
            fail after a while because the site will slow down your speed and eventually give you a connection error.)
        You can also download all m3u8 list to text files by setting M3U8 == True
    '''
    logger = logging.getLogger()
    logger.info(__name__)
    return

def searchVideo(domain, keyword):
    ''' Search domain for videos with keyword, write both a txt and csv with results. You can then use results for downloading.
    '''
    logger = logging.getLogger()
    logger.info(__name__)
    return

def continueDownload(REDOWNLOAD=False):
    ''' Continue your previous download, when REDOWNLOAD == True, erase original copies
    '''
    logger = logging.getLogger()
    logger.info(__name__)
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
