''' Defines single functions to perform menu tasks
'''
import logging
import os

def downloadVideo(uri, DOWNLOAD=True, M3U8=False):
    ''' Download a single video, when DOWNLOAD == False, output video information
    '''
    logger = logging.getLogger(__name__)
    title = ""
    logger.info("%s 下载完成" % title + os.linesep)
    return

def downloadAllVideo(domain, DOWNLOAD=False, M3U8=False):
    ''' Scrape all videos on domain, when DOWNLOAD == True, download them all (this is likely to
            fail after a while because the site will slow down your speed and eventually give you a connection error.)
        You can also download all m3u8 list to text files by setting M3U8 == True
    '''
    return

def searchVideo(domain, keyword):
    ''' Search domain for videos with keyword, write both a txt and csv with results. You can then use results for downloading.
    '''
    return

def continueDownload(REDOWNLOAD=False):
    ''' Continue your previous download, when REDOWNLOAD == True, erase original copies
    '''
    return

   logger.info("1. 下载M3U8列表 | Download M3U8" + os.linesep + "2.查看已存在项目 | Show Existing Projects"
                 + os.linesep + "3.重新下载视频 | Continue" + os.linesep + "4. 合并ts文件 | Merge ts files")

def downloadM3U8(uri):
    ''' Download M3U8 for a single video
    '''
    downloadVideo(uri, DOWNLOAD=False, M3U8=False)
    return

def showProjects():
    ''' Display existing projects by showing directory
    '''
    input("1. 返回 2. 退出")
    return

def reDownload():
    ''' Redownload existing
    '''
    continueDownload(REDOWNLOAD=True)
    return

def mergeTs():
    ''' Merge existing project' ts files into one single ts file
    '''
    return
