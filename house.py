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

from custom_logger import create_logger
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

logger = setup_logger()
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

def parse_deep(video_url, resolution):
    global LOGGER
    global RESOLUTION
    global ERROR_MSG
    global HEADER
    global M3U8
    global DOWNLOAD
    global SEARCH

    # 解析m3u8地址
    start_time = time.time()
    while True:
        try:
            r = requests.get(video_url,headers=HEADER)
            break
        except requests.ConnectionError:
            if time.time() > start_time + CONNECTION_TIMEOUT:
                raise Exception("Unable to get video_url %s \nafter %s seconds of ConnectionErrors" \
                        % (video_url,CONNECTION_TIMEOUT))
            else:
                time.sleep(1)

    video_html = etree.HTML(r.text)
    title = video_html.xpath('//span[@class="title1"]')[0].text # 《命运的X号》剧场公演
    info = video_html.xpath('//span[@class="title2"]')[0].text # TeamX 剧场公演 2018.01.04

    # 文件名
    fname = title
    if not fname.startswith("《"):
        fname = "《" + fname + "》"

    date_string = util.crush_time(info)[:10] # if no date found, use info[:10] part

    fname = date_string + ' ' + fname# 《48狼人杀》 20180202

    if "星梦Mini" in fname:
        fname = fname + ' ' + re.sub('本期成员：', '', re.search(r'.*' + date_string[:4], info).group(0)[:-4])
    if "48狼人杀" in fname or "公演" in fname:
        fname = fname + ' ' + re.search(r'.*' + date_string[:4], info).group(0)[:-4]

    fname = util.clean_string(fname, 'filename')

    chao_url = video_html.xpath('//input[@id="chao_url"]/@value')[0]
    gao_url = video_html.xpath('//input[@id="gao_url"]/@value')[0]
    liuchang_url = video_html.xpath('//input[@id="liuchang_url"]/@value')[0]

    # 默认：超清源
    RESOLUTION = resolution
    if RESOLUTION == 'chaoqing':
        if chao_url == "" or requests.get(chao_url,timeout=CONNECTION_TIMEOUT).text == "\n":
            LOGGER.info("未找到超清源,降低视频清晰度")
            RESOLUTION = "gaoqing"
            m3u8_url = gao_url
        else:
            m3u8_url = chao_url

    if RESOLUTION == 'gaoqing':
        if not gao_url or requests.get(gao_url,timeout=CONNECTION_TIMEOUT,headers=HEADER).text == "\n":
            LOGGER.info("未找到高清源,降低视频清晰度")
            RESOLUTION = "liuchang"
            m3u8_url = liuchang_url
        else:
            m3u8_url = gao_url

    if RESOLUTION == 'liuchang':
        if not liuchang_url or requests.get(liuchang_url,timeout=CONNECTION_TIMEOUT,headers=HEADER).text == "\n":
            LOGGER.info("未找到流畅源,skip current operation: %s", title)
            return {} # return empty object
        else:
            m3u8_url = liuchang_url

    # 解析当页可用视频m3u8
    if M3U8 == '1' or DOWNLOAD == '1':
        ts_list = _get_ts_from_m3u8(m3u8_url)
    else:
        ts_list = []

    LOGGER.info("已解析: %s", fname)
    return {'title':title, 'info':info, 'fname':fname, 'm3u8_url':m3u8_url, 'site_url':video_url, 'ts_list':ts_list}

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
    logger.info("共有%s页" % len(results))
    logger.info("共有%s视频" + os.linesep % sum([len(page) for page in results]))

    all_videos = list(itertools.chain(*videospPage))



    return results

def parse_oneVideo(video, resolution):



results = get_all(domain)[0]
logger.info("total %s pages" % len(results))
logger.info("total %s videos" % sum([len(page) for page in results]))
