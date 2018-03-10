''' snhlivedownloader: a python tool for downloading from live.snh48.com group sites
    usage:
    more info:
'''

from bs4 import BeautifulSoup
import csv
from datetime import datetime
import gevent.pool as pool
import gevent.monkey
import itertools
import json
import logging
import os
import re
import requests
import time
import shutil
import sys

from __adlogger__ import setup_logger
from __variables__ import HEADER
from __variables__ import DOMAIN
from __variables__ import GREENLET_SIZE

from __utilities__ import press_to_exit
from __HTTPrequests__ import get_siteVideoList
from __functions__ import *

def backToMain():
    ''' Return to base Function: snhlivedownload()
    '''
    snhlivedownloader()

def uri_prompt():
    ''' Prompt for uri entry. Do not check for validity of entry.
    '''
    logger = logging.getLogger()
    logger.info("")
    uri = input("请输入视频连接 | Please enter url: ")

    return uri

def domain_prompt():
    ''' Prompt for domain selection, invalid selection lead back to main menu
    '''

    from __variables__ import DOMAIN

    logger = logging.getLogger()
    logger.info("")

    choice = input("请选择网站 | Please choose a site:  1.SNH48   2.GNZ48   3.BEJ48   4.SHY48   5.CKG48  >> ")

    if choice == "1":
        domain = DOMAIN['SNH48']
    if choice == "2":
        domain = DOMAIN['GNZ48']
    elif choice == "3":
        domain = DOMAIN['BEJ48']
    elif choice == "4":
        sitdomain = DOMAIN['SHY48']
    elif choice == "5":
        domain = DOMAIN['CKG48']
    else:
        logger.info('无效输入 | Invalid input')
        backToMain()

    return domain

def search_prompt():
    ''' Prompt for search pattern. Do not check entry validity
    '''
    logger = logging.getLogger()
    logger.info("")
    logger.info("标题关键词搜索 | Search by keywords. 不同关键字通过(,)分割，每个关键字多项必要条件通过(+)添加")
    logger.info("搜索结果储存于 search.txt 和 search.csv 中。如果已有文件，请注意备份。")
    logger.info("   例子1：Team NII + 公演 将筛选 含有Team NII和公演关键字的视频")
    logger.info("   例子2：剧场女神 + Team X, 梦想的旗帜 + Team X 将筛选索 Team X演出的剧场女神 或 梦想的旗帜两场公演视频")
    logger.info("   筛选区域仅限网址展示的标题和副标题" + os.linesep)
    search_pattern = input("请输入关键字 | Search keywords: ")
    logger.info("")

    return search_pattern

def advanced_menu():
    logger = logging.getLogger()

    logger.info("")
    logger.info("高级功能 | Advanced Options")
    logger.info("--------------------------------------------------------------")
    logger.info("1. 下载M3U8列表 | Download M3U8" + os.linesep + "2.查看已存在项目 | Show Existing Projects"
                 + os.linesep + "3.重新下载视频 | Continue" + os.linesep + "4. 合并ts文件 | Merge ts files")
    logger.info("9. 返回 | Return to main menu" + os.linesep + "0. 退出 | Exit" + os.linesep)

    choice = input("您的选择 | Your choice: ")

    while True:
        if choice == '9':
            return 0
        elif choice == '0':
            press_to_exit()
            return 0
        elif choice == '1':
            uri = uri_prompt()
            downloadVideo(uri, DOWNLOAD=False, M3U8=True)
            return 0
        elif choice == '2':
            showProjects()
            return 0
        elif choice == '3':
            continueDownload(REDOWNLOAD=True)
            return 0
        elif choice == '4':
            mergeTs()
            return 0
        else:
            continue

    return 0

def snhlivedownloader():
    ''' Main menu
    '''
    logger = logging.getLogger()

    logger.info("欢迎来到SNH48公演下载器 | Welcome to snhlivedownloader")
    logger.info("--------------------------------------------------------------")
    logger.info("1.下载视频 | Download" + os.linesep + "2.搜索 | Search" + os.linesep + "3.断点续传 | Continue"
                 + os.linesep + "4.遍历全站 | Scrape site" + os.linesep + "5.其它功能 | Advanced")
    logger.info("0. 退出 | Exit" + os.linesep)

    choice = input("您的选择 | Your choice: ")

    if choice == '0':
        sys.exit()
    elif choice == '1': # 下载视频
        uri = uri_prompt()
        downloadVideo(uri)
    elif choice == '2': # 搜索
        domain = domain_prompt()
        search_pattern = search_prompt()
        searchVideo(domain, search_pattern)
    elif choice == '3': # 断点续传
        continueDownload()
    elif choice == '4': # 遍历全站
        domain = domain_prompt()

        # 是否下载M3U8
        logger.info("是否下载全部视频 | Download all videos on site? (默认：否 | Default: No)")
        _choice_ = input("1. 否(no) 2. 是(yes)")
        if _choice_ == '2':
            DOWNLOAD = True
            logger.debug("选择：是(Yes)")
        else:
            DOWNLOAD = False
            logger.debug("选择：否(No)")

        # 是否下载M3U8
        if not DOWNLOAD:
            logger.info("是否下载M3U8 | Download M3U8? (默认：否 | Default: No)")
            _choice_ = input("1. 否(no) 2. 是(yes)")
            if _choice_ == '2':
                M3U8 = True
                logger.debug("选择：是(Yes)")
            else:
                M3U8 = False
                logger.debug("选择：否(No)")

        downloadAllVideo(domain, DOWNLOAD=DOWNLOAD, M3U8=M3U8)

    elif choice == '5':
        advanced_menu()
    else:
        logger.info('无效输入 | Invalid choice')
        logger.info("")
        return 0

    return 0

def test():
    domain = DOMAIN['SNH48']
    logger = logging.getLogger()
    setup_logger()
    gevent.monkey.patch_all()

    from __HTTPrequests__ import get_siteVideoList
    r = get_siteVideoList(domain)
    return r

def main():
    try:
        while True:
            logger = logging.getLogger()
            print(os.linesep * 100)
            logger.info("")
            logger.info(datetime.now().strftime('%Y-%m-%d %H:%M'))
            logger.info("")
            snhlivedownloader()
    except KeyboardInterrupt:
        press_to_exit()

if __name__ == '__main__':
    logger = logging.getLogger()
    setup_logger()
    gevent.monkey.patch_all()
    main()
