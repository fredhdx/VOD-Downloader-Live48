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

import gevent.pool as pool
import gevent.monkey
gevent.monkey.patch_all()

from __variables__ import HEADER

domain = "http://live.snh48.com"
Greenlet_size = 100 # usually 50 would be sufficient for live.snh48.com

def parse_video_deep(video_obj, resolution):
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


def parse_siteurl_deep(video_soup):
    ''' video page soup >> m3u8_url list
    '''
    chao_url = video_soup.find('input', {'id':'chao_url'})['value']
    gao_url = video_soup.find('input', {'id':'gao_url'})['value']
    liuchang_url = video_soup.find('input', {'id':'liuchang_url'})['value']

    m3u8_urls = {'chaoqing': chao_url, 'gaoqing': gao_url, 'liuchang': liuchang_url}

    return m3u8_urls

def parse_soup_basic(video_soup):
    ''' site page soup.each video part >> basic info (title, info, href)
    '''
    site_url = video_soup.find('a')['href']
    img_url = video_soup.find('img')['src']
    title = video_soup.find('h4').text.strip()
    info = video_soup.find('p').text.strip()

    from util import combineTitles
    fname = combineTitles(title, info)

    return {'site_url':site_url, 'img_url':img_url, 'title':title, 'info':info, 'fname':fname}

