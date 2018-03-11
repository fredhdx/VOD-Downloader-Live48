import os
import sys
import shutil
import csv
import json
import logging
import re
import time
import itertools
from datetime import datetime
import requests
from bs4 import BeautifulSoup

import gevent.pool as pool
import gevent.monkey
gevent.monkey.patch_all()

from __variables__ import HEADER

domain = "http://live.snh48.com"
Greenlet_size = 100 # usually 50 would be sufficient for live.snh48.com

def parse_siteurl_deep(video_soup, FULL=False):
    ''' video uri's soup >> m3u8_url list, return dictionary containing information
        return None if any error
    '''
    logger = logging.getLogger()

    try:
        title = video_soup.find('span', {'class':'title1'}).text
        info = video_soup.find('span', {'class':'title2'}).text

        from util import combineTitles
        fname = combineTitles(title, info)

        chao_url = video_soup.find('input', {'id':'chao_url'})['value']
        gao_url = video_soup.find('input', {'id':'gao_url'})['value']
        liuchang_url = video_soup.find('input', {'id':'liuchang_url'})['value']
    except Exception as e:
        logger.info(e)
        return None

    if FULL:
        return {'title':title, 'info':info, 'fname':fname, 'chaoqing': chao_url, 'gaoqing': gao_url, 'liuchang': liuchang_url}
    else:
        return {'chaoqing': chao_url, 'gaoqing': gao_url, 'liuchang': liuchang_url}


def parse_soup_basic(video_soup):
    ''' site page'soup >> each video part >> basic info (title, info, href)
        return None if any error
    '''
    logger = logging.getLogger()

    try:
        site_url = video_soup.find('a')['href']
        title = video_soup.find('h4').text.strip()
        info = video_soup.find('p').text.strip()

        from util import combineTitles
        fname = combineTitles(title, info)
    except Exception as e:
        logger.info(e)
        return None

    return {'site_url':site_url, 'title':title, 'info':info, 'fname':fname}
