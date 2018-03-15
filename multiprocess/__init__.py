''' snhlivedownloader
        a multiprocessing tool for scraping and downloading from live.snh48.com

    Usage: py.exe snhlivedownloader.py

    Required pacakges:
            - requests
            - gevent
            - bs4

    Modules:
        Different functions and helpers are stored in respective sub-files with easily idenfitied names.
        I tried to program all functions with paramater example so they can all be called with parameter unpacking.


    Function status code:
        I tried to catch the execution correctness by arbitary status code, 0 for correct, 1 for otherwise.
        Implementing an arbitary system is based on the consideration that some processes will
        results that are partially correct, and we DO NOT want to interrupt the entire program by Exception.

'''

from bs4 import BeautifulSoup
from datetime import datetime
import gevent.pool as pool
import gevent.monkey
import logging
import os
import re
import time
import shutil
import sys

from __utilities__ import press_to_exit

def script_main():
    ''' main execution script, looped by main() unless interrupted or called to exit()
    '''
    from __functions__ import *
    from __menuANDprompt__ import displayMainMenu
    logger = logging.getLogger()

    status_code = 0

    # Display Main Menu
    my_func, params = displayMainMenu()

    # Execute function
    if my_func:
        execution_results, status_code = my_func(params)
    else:
        return status_code

    return status_code

def main():
    ''' main wrapper: loop script_main()
    '''

    try:
        while True:
            logger = logging.getLogger()
            logger.info(os.linesep + datetime.now().strftime('%Y-%m-%d %H:%M'))
            status_code = script_main()
    except KeyboardInterrupt:
        press_to_exit()

if __name__ == '__main__':
    ''' program entry: set up logger, patch gevent, call main()
    '''

    from __adlogger__ import setup_logger

    logger = logging.getLogger()
    setup_logger()
    gevent.monkey.patch_all()

    print(os.linesep * 100) # clean screen
    logger.info("欢迎来到SNH48公演下载器 | Welcome to snhlivedownloader")
    main()


def test():
    ''' a unit test facility
    '''
    from __variables__ import DOMAIN
    from __adlogger__ import setup_logger

    domain = DOMAIN['SNH48']
    logger = logging.getLogger()
    setup_logger()
    gevent.monkey.patch_all()

    from __HTTPrequests__ import get_siteVideoList
    r = get_siteVideoList(domain)
    return r