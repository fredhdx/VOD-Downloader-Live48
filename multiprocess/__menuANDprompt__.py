import logging
import os
from __utilities__ import press_to_exit

def promptForUri():
    ''' helper: ask for user to enter an url, return an url string
    '''
    logger = logging.getLogger()
    logger.info("")
    uri = input("请输入视频连接 | Please enter url: ")

    return uri

def promptForDomain():
    ''' helper: ask for user to choose a domain (SNH, GNZ, etc), return an url string
    '''

    from __variables__ import DOMAIN

    logger = logging.getLogger()
    logger.info("")

    choice = input("请选择网站 | Please choose a site:  1.SNH48   2.GNZ48   3.BEJ48   4.SHY48   5.CKG48  0.退出 (Exit) >> ")

    while True:
        if choice == "1":
            domain = DOMAIN['SNH48']
            break
        if choice == "2":
            domain = DOMAIN['GNZ48']
            break
        elif choice == "3":
            domain = DOMAIN['BEJ48']
            break
        elif choice == "4":
            domain = DOMAIN['SHY48']
            break
        elif choice == "5":
            domain = DOMAIN['CKG48']
            break
        elif choice == '0':
            press_to_exit()
        else:
            logger.info('无效输入 | Invalid input')
            continue

    return domain

def promptForSearch():
    ''' helper: ask user to enter a search string, return a string
        syntax: case-insensitive; parts separted by \, for OR, \+ for AND
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

def promptForBinary(question, default_value):
    ''' helper: ask user to provide a binary answer for question, return True or False
                question should be a string, default_value should be a bool
          e.g.: question = "Download video?"
                  prompt = "1.Yes 2.No (default)
                  return = True or False

        * the order of choices displayed depends on default_value. The default value choice is
          always the first to be displayed.
    '''
    logger = logging.getLogger()

    logger.info(os.linesep + question)

    if default_value == True:
        choice = input("1.是(yes) 2.否(no)")
        return False if choice == '2' else True
    else:
        choice = input("1.否(no) 2.是(yes)")
        return True if choice == '2' else False

def displayAdvanceMenu():
    ''' menu displayer: ADVANCED menu
                prompt: options
                return:[func_name string, param tuple] piped back to displayMainMenu
    '''

    logger = logging.getLogger() # activate global logger
    my_func = '' # function name string depending on choice
    params = () # function parameter tuple depending on choice

    logger.info("") # always add a new line for display clarity
    logger.info("高级功能 | Advanced Options")
    logger.info("--------------------------------------------------------------")
    logger.info("1. 下载M3U8列表 | Download M3U8" + os.linesep
                + "2.查看已存在项目 | Show Existing Projects" + os.linesep
                + "3.重新下载视频 | Continue" + os.linesep
                + "4. 合并ts文件 | Merge ts files" + os.linesep
                + "9. 返回 | Return to main menu" + os.linesep
                + "0. 退出 | Exit")
    WAIT = True

    while WAIT:
        choice = input(os.linesep + "您的选择 | Your choice: ") # newline first

        if choice == '9':
            WAIT = False
        elif choice == '0':
            press_to_exit()
        elif choice == '1':
            uri = promptForUri()
            my_func = 'downloadAllVideo'
            params = (uri, False, True)
            WAIT = False
            # VideoList = downloadAllVideo(uri, DOWNLOAD=False, M3U8=True)
        elif choice == '2':
            my_func = 'showProjects'
            WAIT = False
        elif choice == '3':
            my_func = 'reDownload'
            WAIT = False
        elif choice == '4':
            my_func = 'mergeTs'
            WAIT = False
        else:
            logger.info('无效输入 | Invalid input')
            continue

    return [my_func, params]

def displayMainMenu():
    ''' menu displayer: Main menu
        prompt: options
        return:[func_name string, param tuple]
    '''
    logger = logging.getLogger()
    my_func = '' # function name string depending on choice. If none, will jump to next iteration
                    # of MAIN EXECUTION LOOP
    params = () # function parameter tuple depending on choice
    WAIT = True

    logger.info("欢迎来到SNH48公演下载器 | Welcome to snhlivedownloader")
    logger.info("--------------------------------------------------------------")
    logger.info("1.下载视频 | Download" + os.linesep
                + "2.搜索 | Search" + os.linesep
                + "3.断点续传 | Continue" + os.linesep
                + "4.遍历全站 | Scrape site" + os.linesep
                + "5.其它功能 | Advanced" + os.linesep
                + "0. 退出 | Exit")

    while WAIT:
        choice = input(os.linesep + "您的选择 | Your choice: ")

        if choice == '0':
            press_to_exit()
        elif choice == '1': # Download video
            uri = promptForUri()
            my_func = 'downloadVideo'
            params = (uri)
            WAIT = False
            # result = downloadVideo(uri)
        elif choice == '2': # search by keyword
            domain = promptForDomain()
            keyword = promptForSearch()
            my_func = 'searchVideo'
            params = (domain, keyword)
            WAIT = False
            # result = searchVideo(domain, search_pattern)
        elif choice == '3': # 断点续传
            my_func = 'continueDownload'
            WAIT = False
            # result = continueDownload()
        elif choice == '4': # download all video
            domain = promptForDomain()

            DOWNLOAD = promptForBinary(os.linesep
                        + "是否下载全部视频 (默认：否) | Download all videos? (Default: No)"
                        , False)
            M3U8 = promptForBinary(os.linesep
                        + "是否下载M3U8 (默认：否) | Download M3U8? (Default: No)"
                        , False)

            my_func = 'downloadAllVideo'
            params = (domain, DOWNLOAD, M3U8)
            WAIT = False

            # results = downloadAllVideo(domain, DOWNLOAD=DOWNLOAD, M3U8=M3U8) # Video list if download any, list of basic info dict otherwise
        elif choice == '5':
            my_func, params = displayAdvanceMenu()
            WAIT = False
        else:
            logger.info('无效输入 | Invalid choice')
            continue

    return [my_func, params]

