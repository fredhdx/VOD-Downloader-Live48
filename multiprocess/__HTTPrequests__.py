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

from __parsing__ import parse_soup_basic
from __parsing__ import parse_siteurl_deep

from __variables__ import GREENLET_SIZE


def _make_HTTPrequests(uri, func_name):
    ''' Using requests.get to make a HTTP get requests, return response if r.status_code == 200
            else return None on any error
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
                return None
            else:
                time.sleep(1)

    if r.status_code == 200:
        return r
    else:
        logger.info("Error: %s" % func_name)
        logger.info(uri)
        logger.info(ERROR_STATUS_CODE % r.status_code)
        return None

def _request_ts_from_uri(m3u8_url):
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
                logger.info("Error: _HTTPrequests_ >> request_ts_from_uri")
                logger.info(ERROR_CONNECTION_TIMEOUT % (m3u8_url, CONNECTION_TIMEOUT))
                return ts_list
            else:
                time.sleep(1)

    if r.status_code != 200:
        logger.info("Error: _HTTPrequests_ >> request_ts_from_uri")
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

def _get_pageList(domain):
    ''' domain >> page url list (sucess: return API_list[], failur: exit)
        return None if error
    '''
    from __variables__ import MAIN_PAGE_API

    API = domain + MAIN_PAGE_API
    pageNum = 1

    r = _make_HTTPrequests(API, "_HTTPrequests_ >> get_pageList")
    if r:
        soup = BeautifulSoup(r.text, 'lxml')
        pageNum = int(re.search(r'\d+', soup.find('span', {'class':'p-skip'}).text).group(0))
    else:
        return None

    API_list = [(API % str(page)) for page in range(1, pageNum + 1)]
    return API_list

def _get_singlePageVideoList(pageUri):
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
                break
        except requests.ConnectionError:
            continue

    if not videos:
        logger.info("Error: _HTTPrequests_ >> get_singlePageVideoList")
        logger.info("Empty list returned by " + pageUri)
        logger.info(ERROR_CONNECTION_TRIALLIMIT % (pageUri, TRIALLIMIT_PER_PAGE))

    return videos

@timefunc
def get_siteVideoList(entryPage_url):
    ''' domain url >> a list of video info dictionary of all videos hosted on site (always return a list containing something)
        timefunc is used for debug, access data by result[0]
        return [] if _get_pageList fails
        [{'site_url':site_url, 'img_url':img_url, 'title':title, 'info':info, 'fname':fname}]
    '''
    from __variables__ import GREENLET_SIZE
    # gevent.monkey.patch_all() # patched in __init__
    logger = logging.getLogger()

    page_list = _get_pageList(entryPage_url)
    if not page_list:
        return []

    s = requests.session()
    s.headers.update(HEADER)
    p = pool.Pool(GREENLET_SIZE)
    videospPage = p.map(_get_singlePageVideoList, page_list)
    p.join()
    s.close()

    logger.info(os.linesep + '%s 读取完毕' % entryPage_url)
    logger.info("共有%s页" % len(videospPage))
    logger.info("共有%s视频" % sum([len(page) for page in videospPage]) + os.linesep )

    all_videos = list(itertools.chain(*videospPage))

    return all_videos

def get_batch_M3U8(videoObjects, resolution):
    ''' List of SnhVideo objects (might contain None objects) >> get their M3U8
        return [] containg 0 or -1, -1 indicating failure, 0 indicating success
    '''
    def _download_tslist(videoobject, resolution):
        ''' return 0 on success, -1 on failure
        '''

        if videoobject:
            videoobject.set_res(resolution)
            r = videoobject.get_tslist()
        else:
            return -1

        return r

    s = requests.session()
    s.headers.update(HEADER)
    p = pool.Pool(GREENLET_SIZE)

    results = p.map(_download_tslist, zip(videoObjects, [resolution] * len(videoObjects)))
    p.join()
    s.close()

    return results

def _uri_to_video(uri):
    ''' make a request to uri, create corresponding SnhVideo object
        return video on success, None on failure
    '''
    r = _make_HTTPrequests(uri, "__HTTPrequests__ >> _uri_to_vdeo")
    if r:
        soup = BeautifulSoup(r.text, 'lxml')
        _video_ = Snh48Video()
        parsed = parse_siteurl_deep(soup)
        if parsed:
            _video_.update(parsed)
            return _video_
        else:
            return None

def _urls_to_videos(urls):
    ''' a list of urls >> a list of SnhVideo objects, might contain None objects
    '''
    s = requests.session()
    s.headers.update(HEADER)
    p = pool.Pool(GREENLET_SIZE)

    results = p.map(_uri_to_video, urls)

    return results
