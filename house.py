import os
import sys
import shutil
import csv
import json
import re
import time
import itertools
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import util
import logging
from custom_logger import setup_logger

import gevent.pool as pool
import gevent.monkey
gevent.monkey.patch_all()


HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) \
    AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/35.0.1916.114 Safari/537.36'
    }

domain = "http://live.snh48.com"
Greenlet_size = 100 # usually 50 would be sufficient for live.snh48.com

logging.getLogger()
setup_logger()
logger = logging.getLogger()
logging.info(datetime.now().strftime('%Y-%m-%d %H:%M'))

def get_pageList(domain):

    API = domain + '/index/index/p/%s' + '.html'
    pageNum = 1

    try:
        r = requests.get(domain, headers=HEADER)
        if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'lxml')
                pageNum = int(re.search(r'\d+', soup.find('span', {'class':'p-skip'}).text).group(0))
    except Exception as e:
        logger.error(e, exc_info = True)

    API_list = [(API % str(page)) for page in range(1, pageNum + 1)]
    return API_list

def parse_basic(video):
    href = video.find('a')['href']
    img_src = video.find('img')['src']
    title1 = video.find('h4').text.strip()
    title2 = video.find('p').text.strip()

    from util import combineTitles
    title = combineTitles(title1, title2)

def get_completeVideoList(domain):
    ''' Return a list of video objects
    '''

    def get_singlePage(pageUrl):
        videos = []
        trialLimit = 10
        try:
            for count in range(trialLimit):
                r = requests.get(pageUrl, headers=HEADER)
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, 'lxml')
                    videos = soup.findAll('li', {'class':'videos'})
                    if len(videos) == 0:
                        continue
                    break
                if count == trialLimit - 1:
                    logger.info('get_all: %s receives %s respons' % r.status_code)
        except Exception as e:
            logger.info('get_all: ' + e, exc_info = True)

        return videos

    page_list = get_pageList(domain)
    s = requests.session()
    s.headers.update(HEADER)
    p = pool.Pool(Greenlet_size)
    videospPage = p.map(get_singlePage, page_list)
    p.join()
    s.close()

    logger.info(os.linesep + '%s读取完毕' % domain)
    logger.info("共有%s页" % len(videospPage))
    logger.info("共有%s视频" % sum([len(page) for page in videospPage]) + os.linesep )

    all_videos = list(itertools.chain(*videospPage))
    logger.info("Flattened: %s" % len(all_videos))
    return all_videos


results = get_completeVideoList(domain)[0]