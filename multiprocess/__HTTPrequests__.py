from bs4 import BeautifulSoup
import gevent.pool as pool
import gevent.monkey
import itertools
import logging
import os
import requests
import re
import sys
import time

from __variables__ import HEADER
from __variables__ import CONNECTION_TIMEOUT
from __variables__ import ERROR_CONNECTION_TIMEOUT, ERROR_STATUS_CODE, ERROR_CONNECTION_TRIALLIMIT

from __snhvideo__ import Snh48Video
from __utilities__ import timefunc
from __utilities__ import press_to_exit

from __parsing__ import parse_soup_basic
from __parsing__ import parse_siteurl_deep



def make_HTTPrequests(uri, func_name):
    ''' Using requests.get to make a HTTP get requests, return response if r.status_code == 200
            else exit on error
    '''
    logger = logging.getLogger()

    start_time = time.time()
    while True:
        try:
            r = requests.get(uri % '1', headers=HEADER)
            break
        except requests.ConnectionError:
            if time.time() > start_time + CONNECTION_TIMEOUT:
                logger.info("Error: %s" % func_name)
                logger.info(ERROR_CONNECTION_TIMEOUT % (uri, CONNECTION_TIMEOUT))
                sys.exit()
            else:
                time.sleep(1)

    if r.status_code == 200:
        return r
    else:
        logger.info("Error: %s" % func_name)
        logger.info(uri)
        logger.info(ERROR_STATUS_CODE % r.status_code)
        sys.exit()

def get_pageList(domain):
    ''' domain >> page url list (sucess: return API_list[], failur: exit)
    '''
    from __variables__ import MAIN_PAGE_API

    API = domain + MAIN_PAGE_API
    pageNum = 1

    r = make_HTTPrequests(API, "_HTTPrequests_ >> get_pageList")
    soup = BeautifulSoup(r.text, 'lxml')
    pageNum = int(re.search(r'\d+', soup.find('span', {'class':'p-skip'}).text).group(0))

    API_list = [(API % str(page)) for page in range(1, pageNum + 1)]
    return API_list

def get_singlePageVideoList(pageUri):
    ''' page url >> video info dictionary list (success: return videos[]  failure: return [])
        {'site_url':site_url, 'img_url':img_url, 'title':title, 'info':info, 'fname':fname}
    '''
    from __variables__ import TRIALLIMIT_PER_PAGE

    logger = logging.getLogger()
    videos = []

    for count in range(TRIALLIMIT_PER_PAGE):
        try:
            r = requests.get(pageUri, headers=HEADER)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'lxml')
                videos = soup.findAll('li', {'class':'videos'})
                if len(videos) == 0:
                    continue
                videos = [parse_soup_basic(soup) for soup in videos]
                break
            if count == TRIALLIMIT_PER_PAGE - 1:
                logger.info('Error: _HTTPrequests_ >> get_singlePageVideoList')
        except requests.ConnectionError:
            continue

    if not videos:
        logger.info("Error: _HTTPrequests_ >> get_singlePageVideoList")
        logger.info("Empty list returned by " + pageUri)
        logger.info(ERROR_CONNECTION_TRIALLIMIT % (pageUri, TRIALLIMIT_PER_PAGE))

    return videos

@timefunc
def get_siteVideoList(entryPage):
    ''' domain >> a list of video info dictionary of all videos hosted on site (always return a list containing something)
        timefunc is used for debug, access data by result[0]
    '''
    from __variables__ import GREENLET_SIZE
    # gevent.monkey.patch_all() # patched in __init__
    logger = logging.getLogger()

    page_list = get_pageList(entryPage)
    s = requests.session()
    s.headers.update(HEADER)
    p = pool.Pool(GREENLET_SIZE)
    videospPage = p.map(get_singlePageVideoList, page_list)
    p.join()
    s.close()

    logger.info(os.linesep + '%s 读取完毕' % entryPage)
    logger.info("共有%s页" % len(videospPage))
    logger.info("共有%s视频" % sum([len(page) for page in videospPage]) + os.linesep )

    all_videos = list(itertools.chain(*videospPage))

    return all_videos

def download_ts_from_uri(m3u8_url):
    ''' downlaod ts list from m3u8 url (success: return list, failure return [])
    '''

    logger = logging.getLogger()
    ts_list = []

    if not "m3u8" in m3u8_url:
        logger.info('Error download_ts_from_uri: path contains no m3u8 tag')
        logger.info('m3u8_url: %s' % m3u8_url)
        return ts_list

    start_time = time.time()
    while True:
        try:
            r = requests.get(m3u8_url, headers=HEADER)
            break
        except requests.ConnectionError:
            if time.time() > start_time + CONNECTION_TIMEOUT:
                logger.info("Error: _HTTPrequests_ >> download_ts_from_uri")
                logger.info(ERROR_CONNECTION_TIMEOUT % (m3u8_url, CONNECTION_TIMEOUT))
                break
            else:
                time.sleep(1)

    if r.status_code != 200:
        logger.info("Error: _HTTPrequests_ >> download_ts_from_uri")
        logger.info("%s" % m3u8_url)
        logger.info(ERROR_STATUS_CODE % r.status_code)
        return ts_list

    text = r.text.splitlines()
    base_uri = m3u8_url.rsplit('/', 1)[0] # for old stream,　this is the .mp4 link

    for i in range(0, len(text)):
        if "#EXTINF" in text[i]:
            rel_link = text[i+1]

            if "http" in rel_link:
                ts_list.append({'EXTINF':text[i], 'ts_url':rel_link})
            else:
                ts_list.append({'EXTINF':text[i], 'ts_url':base_uri + '/' + rel_link})

    return ts_list

def _uri_to_video(uri):
    ''' make a request to uri, create corresponding SnhVideo object
    '''
    from __parsing__ import parse_soup_basic

    logger = logging.getLogger()

    start_time = time.time()
    while True:
        try:
            r = requests.get(uri, headers=HEADER)
            break
        except requests.ConnectionError:
            if time.time() > start_time + CONNECTION_TIMEOUT:
                logger.info(ERROR_CONNECTION_TIMEOUT % (uri, CONNECTION_TIMEOUT))
                sys.exit()
            else:
                time.sleep(1)

    _video_ = Snh48Video()
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'lxml')
        _basic_ = parse_soup_basic(soup)
        _video_.update(_basic_)
    else:
        logger.info("Error: _HTTPrequests_ >> _uri_to_video")
        logger.info(uri)
        logger.info(ERROR_STATUS_CODE % r.status_code)
        sys.exit()

    while True:
        try:
            r = requests.get(_video_.site_url, headers=HEADER)
            break
        except requests.ConnectionError:
            if time.time() > start_time + CONNECTION_TIMEOUT:
                logger.info(ERROR_CONNECTION_TIMEOUT % (uri, CONNECTION_TIMEOUT))
                sys.exit()
            else:
                time.sleep(1)

    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'lxml')
        m3u8_urls = parse_siteurl_deep(soup)
        _video_.update(m3u8_urls)
    else:
        logger.info("Error: _HTTPrequests_ >> _uri_to_video")
        logger.info(uri)
        logger.info(ERROR_STATUS_CODE % r.status_code)
        sys.exit()

    return 0