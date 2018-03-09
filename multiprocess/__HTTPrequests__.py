from bs4 import BeautifulSoup
import gevent.pool as pool
import gevent.monkey
import itertools
import logging
import os
import requests
import re

from __variables__ import HEADER

logger = logging.getLogger(__name__)

def get_pageList(pageUrl):
    ''' Retrieve a list of urls for all video pages on live.snh48.com. updated 2018/03/08
        Perform 1 requests.get
    '''
    from __variables__ import MAIN_PAGE_API
    API = domain + MAIN_PAGE_API
    pageNum = 1

    try:
        r = requests.get(pageUrl, headers=HEADER)
        if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'lxml')
                pageNum = int(re.search(r'\d+', soup.find('span', {'class':'p-skip'}).text).group(0))
    except Exception as e:
        logger.error(e, exc_info = True)

    API_list = [(API % str(page)) for page in range(1, pageNum + 1)]
    return API_list

def get_singlePageVideoList(pageUri):
    ''' Return a list of urls of all videos on 1 page of live.snh48.com
    '''
    from __variables__ import TRIAL_LIMIT_PER_PAGE
    videos = []

    try:
        for count in range(TRIAL_LIMIT_PER_PAGE):
            r = requests.get(pageUri, headers=HEADER)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'lxml')
                videos = soup.findAll('li', {'class':'videos'})
                if len(videos) == 0:
                    continue
                break
            if count == TRIAL_LIMIT_PER_PAGE - 1:
                logger.debug('get_completeVideoList >> get_singlePage: requests error, status code: %s.' % r.status_code)
    except Exception as e:
        logger.debug('get_completeVideoList: ' + e, exc_info = True)

    return videos

def get_siteVideoList(entryPage):
    ''' Return a list of urls of all videos hosted on live.snh48.com group sites
        Using gevent.pool with pool size = GREENLET_SIZE
        Info: list is flattened by page order: [page1 videos + page2 videos + ... + pageLast videos]
    '''
    from __variables__ import GREENLET_SIZE
    # gevent.monkey.patch_all() # patched in __init__

    page_list = get_pageList(entryPage)
    s = requests.session()
    s.headers.update(HEADER)
    p = pool.Pool(GREENLET_SIZE)
    videospPage = p.map(get_singlePageVideoList, page_list)
    p.join()
    s.close()

    logger.info(os.linesep + '%s读取完毕' % entryPage)
    logger.info("共有%s页" % len(videospPage))
    logger.info("共有%s视频" % sum([len(page) for page in videospPage]) + os.linesep )

    all_videos = list(itertools.chain(*videospPage))
    logger.info("Flattened: %s" % len(all_videos))
    return all_videos