#!/usr/bin/python3
# coding:utf-8 #
"""
    下载live.snh48.com历史视频"
              + 采用python3: requests库"
     　　     + 支持断点续传"
              + 可选择单个视频或爬取所有视频"
              + 可选取清晰度"
              + 可输出m3u8片段列表(需要简单修改参数)"

    参考: https://github.com/ShizukuIchi/avgle-downloader/"
          https://pypi.python.org/pypi/m3u8"
          https://github.com/huzhenjie/m3u8_downloader"
          https://gist.github.com/vladignatyev/ "
"""

import os
import sys
import csv
import time
import requests
import shutil
import re
import util
from lxml import etree

HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) \
    AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/35.0.1916.114 Safari/537.36',
    'Cookie': 'AspxAutoDetectCookieSupport=1'
}


SINGLE = '0'
SHOW = '0'
MERGE_TS = '0'
SINGLE_CONTINUE = '0'
RE_DOWNLOAD = '0'
DOWNLOAD = '1'
RESOLUTION = 'chaoqing'
SNH48LIVE_API = "http://live.snh48.com"

# 是否为每个视频解析ts地址
M3U8 = '0'

CONNECTION_TIMEOUT = 90
ERROR_MSG = []

# 进度条
def progressbar(count, total, status=''):
    """ show progressbar.
    """
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar_str = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar_str, percents, '%', status))
    sys.stdout.flush()

# 对象定义
class snh48_video:
    """ Class: snh48_video.
    """
    def __init__(self):
        self.title = ''
        self.info = ''
        self.fname = ''
        self.m3u8_url = ''
        self.site_url = ''
        self.ts_list = {}
        self.img_url = ''

    def update(self, args):
        """ update snh48_video content.
        """

        if not args:
            print("Error: snh48_video.update(args): empty args")
            sys.exit(1)
        else:
            for k_args in args:
                if k_args == 'title':
                    self.title = args['title']
                elif k_args == 'info':
                    self.info = args['info']
                elif k_args == 'fname':
                    self.fname = args['fname']
                elif k_args == 'm3u8_url':
                    self.m3u8_url = args['m3u8_url']
                elif k_args == 'site_url':
                    self.site_url = args['site_url']
                elif k_args == 'ts_list':
                    self.ts_list = args['ts_list']
                else:
                    print("Warning: key %s not found in snh48_video" % k_args)

    def addimgurl(self, imgurl):
        """ add imgurl to class.
        """

        if not imgurl:
            self.img_url = imgurl

    def write_tslist(self, path):
        """ write video tslist, if exist, to file.
        """

        if not path:
            print("Error: snh48_video.write_tslist(path): empty path")
            sys.exit(1)
        else:
            path = path + os.path.sep + self.fname + '.m3u8'

        import traceback
        try:
            f = open(path, 'wt')
        except OSError as e:
            print(e)
            traceback.print_exc()
            sys.exit(1)

        if not self.ts_list:
            print("Error: empty ts_list for %s %s" % (self.title, self.info))
        else:
            for line in self.ts_list:
                f.write(line['ts_url'] + '\n')
        f.close()

    def download(self, path):
        """ Downlaod video content to /title/tmp/ as ts fragments.
        """

        if not path:
            print("Error: snh48_video.download(path): empty path")
            sys.exit(1)
        else:
            # create directory
            path = path + os.path.sep + self.fname + os.path.sep + RESOLUTION

            if not os.path.isdir(path + os.path.sep + 'tmp'):
                os.makedirs(path + os.path.sep +'tmp')


            # create or update info.txt to save parsed info
            ipath = path + os.path.sep + "info.txt"
            with open(ipath, 'w') as f:
                f.write("video_url: %s\n" % self.site_url)
                f.write("title: %s\n" % self.title)
                f.write("info: %s\n" % self.info)
                f.write("m3u8_url: %s\n" % self.m3u8_url)
                f.write("resolution: %s" % RESOLUTION)

            # write ts list
            self.write_tslist(path)

            # download file
            index = 1
            ts_list_len = len(self.ts_list)
            tsNames = []
            for ts_file in self.ts_list:
                tmp_path = path + os.path.sep + 'tmp'
                tmp_name = path + os.path.sep + 'tmp' + os.path.sep + str(index) + '.ts'
                tmp_files = [name for name in os.listdir(tmp_path)
                             if os.path.isfile(os.path.join(tmp_path, name))]

                progressbar(index, ts_list_len, status="正在写入: %s/%d" % (tmp_name.rsplit(os.path.sep)[-1], len(self.ts_list)))

                # check file exist
                # 总是试图下载上次停止的最后一个文件
                file_exist = os.path.isfile(tmp_name)
                file_index = self.ts_list.index(ts_file) + 1
                existing_count = len([name for name in tmp_files if name.endswith('.ts')])

                if (not file_exist) or (file_exist and file_index == existing_count):
                    start_time = time.time()
                    while True:
                        try:
                            r = requests.get(ts_file['ts_url'], stream=True)
                            break
                        except requests.ConnectionError:
                            if time.time() > start_time + CONNECTION_TIMEOUT:
                                raise Exception('Unable to connect %s after %s seconds of ConnectionErrors' \
                                        % (ts_file['title'], CONNECTION_TIMEOUT))
                            else:
                                time.sleep(1)

                    if r.status_code == 200:
                        with open(tmp_name, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=512 * 1024):
                                if chunk:
                                    f.write(chunk)
                    else:
                        print("\nsnh48_video.download: write_ts: connection error")
                        sys.exit(1)

                tsNames.append(tmp_name)
                index += 1

            print('All .ts files downloaded for: ' + self.fname)

            if index == len(self.ts_list) + 1:
                with open(path + os.path.sep + self.fname, 'wb') as f:
                    for ts in tsNames:
                        with open(ts, 'rb') as mergefile:
                            shutil.copyfileobj(mergefile, f)
                        os.remove(ts)
                    print('%s merged' % self.fname)
            else:
                print('Merge failed for %s' % self.fname)

# 显示目录树
def list_directory(input_path, hidden=None):
    startpath = os.getcwd() if not input_path else input_path
    if not os.path.isdir(startpath):
        print("显示目录树:文件夹不存在 %s" % startpath)
        sys.exit(1)
    MAX_WIDTH = 100
    print()
    print('#' * MAX_WIDTH)
    index = 1
    menu_list = []
    show_list = []
    max_level = 0
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)

        if os.path.basename(root)[:2] != '__':
            _menu_item = '# {}. {}{}/'.format(index, indent, os.path.basename(root))
            index += 1

        # subindent = ' ' * 4 * (level + 1)
        # for f in files:
            # print('{}{}'.format(subindent, f))
            if files:
                file_word = 'Total {} files -> {}'.format(len(files), files[0])
                separator = MAX_WIDTH - len(_menu_item) - len(file_word) - 2
                _menu_item = _menu_item + ' ' + ' ' * separator + ' ' + file_word

            menu_list.append({'root':root, 'dirs':dirs, 'files':files})
            if hidden is not None:
                if hidden not in _menu_item:
                    #print(_menu_item)
                    show_list.append({'item':_menu_item, 'level': level})
            else:
                #print(_menu_item)
                show_list.append({'item':_menu_item, 'level': level})

            max_level = level if max_level<level else max_level

    for menu_display_item in show_list:
        if menu_display_item['level'] == 1:
            print()

        print(menu_display_item['item'])

    _menu_item = '# {}. {}{} (custom)/'.format(index, '', input_path)
    menu_list.append({'root':input_path, 'dirs':[], 'files':[]})
    print('#' * MAX_WIDTH)

    return menu_list

# 合并ts文件
def merge_ts(path):
    print("手动合并ts文件,请选择工作文件夹")
    menu_list = list_directory(path)

    while True:
        choice = input("选择文件夹(选0退出): ")
        if choice == '0': break
        elif choice in [str(i) for i in range(1, len(menu_list))]:
            _chosen = menu_list[int(choice)-1]['root']
            print(_chosen)

            empty = '1'
            for fn in os.listdir(_chosen):
                if fn.endswith('.ts'):
                    empty = '0'

            if empty == '1':
                print("警告:文件夹不包含任何.ts文件 -> 重新选择")
                continue

            print("选择：{}".format(_chosen))
            working_path = _chosen
            break

    # 开始合并
    if working_path == '':
        print("路径错误: {}".format(working_path))
        sys.exit(1)

    files = [f for f in os.listdir(working_path) if f.endswith('.ts')]
    tsNames = sorted(files, key=lambda f: int(f.split('.')[0]))
    title = working_path.split(os.path.sep)[-3]
    with open(os.path.sep.join(working_path.split(os.path.sep)[:-1]) + os.path.sep + title + '.ts', 'wb') as f:
        for ts in tsNames:
            with open(working_path + os.path.sep + ts, 'rb') as mergefile:
                shutil.copyfileobj(mergefile, f)
            # os.remove(ts)
        print('%s merged' % title)

# 解析m3u8文件
def _get_ts_from_m3u8(m3u8_url):
    global ERROR_MSG
    global HEADER

    if not "m3u8" in m3u8_url:
        print('_get_ts_from_m3u8 error: path contains no m3u8 tag')
        sys.exit(1)

    start_time = time.time()
    while True:
        try:
            r = requests.get(m3u8_url, headers=HEADER)
            break
        except requests.ConnectionError:
            if time.time() > start_time + CONNECTION_TIMEOUT:
                raise Exception("Unable to get m3u8 list %s \nafter %s seconds of ConnectionErrors" \
                        % (m3u8_url, CONNECTION_TIMEOUT))
            else:
                time.sleep(1)

    if r.status_code != 200:
        print("_get_ts_from_m3u8 connection status_code: " + str(r.status_code))
        print("skip this operation")
        ERROR_MSG.append({m3u8_url:"connection code: " + str(r.status_code)})
        return []

    text = r.text.splitlines()
    base_uri = m3u8_url.rsplit('/', 1)[0] # for old stream,　this is the .mp4 link

    ts_list = []

    for i in range(0, len(text)):
        if "#EXTINF" in text[i]:
            rel_link = text[i+1]

            if "http" in rel_link:
                ts_list.append({'EXTINF':text[i], 'ts_url':rel_link})
            else:
                ts_list.append({'EXTINF':text[i], 'ts_url':base_uri + '/' + rel_link})

    return ts_list

# 自动继续下载已存在视频
def _continue_download(path):

    menu_list = list_directory(path, hidden="tmp")

    _chosen = ""
    while True:
        choice = input("请选择'清晰度'层级,如: gaoqing\n选择文件夹(选0退出):")
        if choice == '0': sys.exit()
        elif choice in [str(i) for i in range(1, len(menu_list))]:
            _chosen = menu_list[int(choice)-1]['root']

            tmp_path = _chosen + os.path.sep + "tmp"
            tmp_files = [name for name in os.listdir(tmp_path) if os.path.isfile(os.path.join(tmp_path, name))]
            tmp_files = [name for name in tmp_files if name.endswith('.ts')]
            if (os.path.isdir(tmp_path) and len(tmp_files) > 0):
                print(_chosen)
                break
            else:
                print("自动断点续传: 没找到《%s》ts临时文件，请检查已下载部分是否存在\n" %
                      _chosen.split(os.path.sep)[-2])
                sys.exit()

    info_file = _chosen + os.path.sep + "info.txt"
    url = ""
    res = ""
    if os.path.isfile(info_file):
        with open(info_file, 'r') as f:
            for line in f.readlines():
                if "video_url" in line:
                    url = line.split(": ")[1].strip()
                if "resolution" in line:
                    res = line.split(": ")[1].strip()

            print("为《%s》找到链接：%s at %s" % (_chosen.split(os.path.sep)[-2], url, res))
    else:
        print("自动断点续传: 没找到《%s》info.txt信息文件，请检查已下载部分是否存在\n"
              % _chosen.split(os.path.sep)[-2])
        sys.exit()

    if not "live.snh48.com" in url:
        print("自动断点续传: 没找到《%s》有效链接，请手动输入网址\n" % _chosen.split(os.path.sep)[-2])
        sys.exit()

    parsed = _get_downloadable_from_url(url, res)
    parsed_fname = parsed['fname']
    if parsed_fname != _chosen.split(os.path.sep)[-2]:
        print("自动断点续传：已存在视频和远程视频不一致")
        print("------------------  有可能覆盖错误视频")
        print("请检查info.txt中的网址是否指向目标视频")
        print("已存在：%s" % _chosen.split(os.path.sep)[-2])
        print("远程文件：%s" % parsed_title)
        print("退出")
        sys.exit()

    return [url, res]

# 重新下载已存在视频
def _force_redownload(path):

    menu_list = list_directory(path, hidden="tmp")

    _chosen = ""
    while True:
        choice = input("请选择'清晰度'层级,如: gaoqing\n选择文件夹(选0退出):")
        if choice == '0': sys.exit()
        elif choice in [str(i) for i in range(1, len(menu_list))]:
            _chosen = menu_list[int(choice)-1]['root']
            break

    info_file = _chosen + os.path.sep + "info.txt"
    url = ""
    res = ""
    if os.path.isfile(info_file):
        with open(info_file, 'r') as f:
            for line in f.readlines():
                if "video_url" in line:
                    url = line.split(": ")[1].strip()
                if "resolution" in line:
                    res = line.split(": ")[1].strip()

            print("为《%s》找到链接：%s at %s" % (_chosen.split(os.path.sep)[-2], url, res))
    else:
        print("重新下载已存在视频: 没找到《%s》info.txt信息文件，请通过单个视频选项下载\n"
              % _chosen.split(os.path.sep)[-2])
        sys.exit()

    if not "live.snh48.com" in url:
        print("重新下载已存在视频: 没找到《%s》有效链接，请检查信息文件\n" % _chosen.split(os.path.sep)[-2])
        sys.exit()

    parsed = _get_downloadable_from_url(url, res)
    parsed_fname = parsed['fname']
    if parsed_fname != _chosen.split(os.path.sep)[-2]:
        print("重新下载已存在视频：已存在的视频和远程视频不一致")
        print("------------------  有可能覆盖错误视频")
        print("请检查info.txt中的网址是否指向目标视频")
        print("已存在：%s" % _chosen.split(os.path.sep)[-2])
        print("远程文件：%s" % parsed_title)
        print("退出")
        sys.exit()

    tmp_path = _chosen + os.path.sep + "tmp"
    if os.path.isdir(tmp_path):
        choice = input("警告：重新下载《%s》-%s 视频将删除tmp文件夹所有下载片段\n1.继续 2.退出(默认)"
                       % (_chosen.split(os.path.sep)[-2], res))
        if choice == '1':
            tmp_files = [name for name in os.listdir(tmp_path) if os.path.isfile(os.path.join(tmp_path, name))]
            tmp_files = [os.path.join(tmp_path,name) for name in tmp_files]
            for _file in tmp_files:
                try:
                    os.remove(_file)
                except OSError as e:
                    print(e)
                    sys.exit(1)
            print("tmp文件夹已清空")
        else:
            print("退出")
            sys.exit()
    return [url,res]


# 解析单个视频
def _get_downloadable_from_url(video_url, resolution):
    global RESOLUTION
    global ERROR_MSG
    global HEADER

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
            print("未找到超清源,降低视频清晰度")
            RESOLUTION = "gaoqing"
            m3u8_url = gao_url
        else:
            m3u8_url = chao_url

    if RESOLUTION == 'gaoqing':
        if not gao_url or requests.get(gao_url,timeout=CONNECTION_TIMEOUT,headers=HEADER).text == "\n":
            print("未找到高清源,降低视频清晰度")
            RESOLUTION = "liuchang"
            m3u8_url = liuchang_url
        else:
            m3u8_url = gao_url

    if RESOLUTION == 'liuchang':
        if not liuchang_url or requests.get(liuchang_url,timeout=CONNECTION_TIMEOUT,headers=HEADER).text == "\n":
            print("未找到流畅源,skip current operation: {}".format(title))
            ERROR_MSG.append({'error: ':'清晰度{}未找到:{}'.format(RESOLUTION,title)})
            return {} # return empty object
        else:
            m3u8_url = liuchang_url

    # 解析当页可用视频m3u8
    ts_list = _get_ts_from_m3u8(m3u8_url)

    print("已解析: %s" % fname)
    return {'title':title, 'info':info, 'fname':fname, 'm3u8_url':m3u8_url, 'site_url':video_url, 'ts_list':ts_list}

# 下载live.snh视频
def spider_snhLive():

    global SHOW
    global DOWNLOAD
    global RESOLUTION
    global MERGE_TS
    global SINGLE
    global SINGLE_CONTINUE
    global RE_DOWNLOAD
    global ERROR_MSG
    global HEADER
    global M3U8

    print("爬取live.snh48视频?(默认：全网)")
    print("--------------------------------------------------------------")
    print("1. 单个视频 2.网站 3.自动断点续传 4.重新下载已存在视频 5.查看已存在项目 6.合并ts文件")
    choice = input("您的选择:")
    if choice == '5':
        SHOW = '1'
    elif choice == '1':
        SINGLE = '1'
        print("爬取: 单个视频")
    elif choice == '3':
        SINGLE_CONTINUE = '1'
        print("自动断点续传")
    elif choice == '4':
        RE_DOWNLOAD = '1'
        print('重新下载已存在视频')
    elif choice == '6':
        MERGE_TS = '1'
    else:
        SINGLE = '0'
        print("爬取: 网站")

    print("--------------------------------------------------------------")
    choice = input("工作文件夹（当前 + 输入, 默认 /snh48live）:")
    if not choice:
        working_path = os.getcwd() + '/snh48live'
    else:
        choice = choice[1:] if choice[0] == os.path.sep else choice
        working_path = os.getcwd() + os.path.sep + choice
    print("工作文件夹: %s" % working_path)

    if SHOW == '1':
        list_directory(working_path)
        sys.exit()

    if MERGE_TS == '1':
        merge_ts(working_path)
        sys.exit()

    if not os.path.isdir(working_path) and SINGLE_CONTINUE == '0' and RE_DOWNLOAD == '0':
        choice = input("工作文件夹不存在，是否创立: 1.是 2.否（默认）")
        if choice == '1':
            os.makedirs(working_path)
        else:
            sys.exit()
    elif not os.path.isdir(working_path) and (SINGLE_CONTINUE == '1' or RE_DOWNLOAD == '1'):
        print("工作文件夹不存在，退出")
        sys.exit()

    if SINGLE_CONTINUE == '0' and RE_DOWNLOAD == '0':
        print("--------------------------------------------------------------")
        print("下载视频？(默认:是)")
        print("1. 是 2.否")
        choice = input("选择:")
        if choice == "2":
            DOWNLOAD = '0'
        else:
            DOWNLOAD = '1'


        print("--------------------------------------------------------------")
        print("选择清晰度？(未输入默认为:超清)")
        print("1. 超清 2.高清 3.流畅")
        choice = input("选择:")
        if choice == '2':
            RESOLUTION = 'gaoqing'
        elif choice == '3':
            RESOLUTION = 'liuchang'
        else:
            RESOLUTION = 'chaoqing'
        print("清晰度: %s" % RESOLUTION)

    if SINGLE_CONTINUE == '1':
        video_url, RESOLUTION = _continue_download(working_path)
    elif RE_DOWNLOAD == '1':
        video_url, RESOLUTION = _force_redownload(working_path)
    elif SINGLE == '1':
        print("--------------------------------------------------------------")
        video_url = input("请输入单个视频地址(live.snh48.com):")
        if not video_url:
            print("需要输入视频地址,请重新开始")
            sys.exit(1)

    if SINGLE == '1' or SINGLE_CONTINUE == '1' or RE_DOWNLOAD == '1':
        parsed = _get_downloadable_from_url(video_url, RESOLUTION)
        if bool(parsed):
            video_obj = snh48_video()
            video_obj.update(parsed)
            if DOWNLOAD == '1':
                video_obj.download(working_path)

            # print info
            outline = 'title: ' + video_obj.title + '\ninfo: ' + video_obj.info \
                    + '\nfname: ' + fname \
                    + '\nurl: ' + video_obj.site_url + '\nm3u8_url: ' + video_obj.m3u8_url
            print(outline)
    else:
        print("--------------------------------------------------------------")
        print("解析所有视频(live.snh48.com)")
        print("--------------------------------------------------------------")
        print("是否为每个视频建立.ts列表?")
        M3U8 = input("1. 是 2.否 (默认: 否)")
        if M3U8 == '1':
            print("列表储存在: " + working_path + os.path.sep + 'M3U8' + os.path.sep + RESOLUTION)
            print()

        PAGE_START = input("从第几页开始(未输入默认:1):")
        PAGE_START = 1 if PAGE_START == "" else int(PAGE_START)
        VIDEO_START = input("从第几个视频开始(未输入默认:1):")
        VIDEO_START = 1 if VIDEO_START == "" else int(VIDEO_START)

        site_url = SNH48LIVE_API

        start_time = time.time()
        while True:
            try:
                r = requests.get(site_url,headers=HEADER)
                break
            except requests.ConnectionError:
                if time.time() > start_time + CONNECTION_TIMEOUT:
                    raise Exception("Unable to get %s \nafter %s seconds of ConnectionErrors" \
                            % (site_url,CONNECTION_TIMEOUT))
                else:
                    time.sleep(1)

        index_html = etree.HTML(r.text)

        # 获取页面总数
        num = int(index_html.xpath('//a[@class="end"]')[0].text)
        print("共%d页" % num)
        print("--------------------------------------------------------------")

        if PAGE_START > num:
            print("PAGE_START %d 超出范围(共%d页)" % (PAGE_START,num))
            sys.exit(1)

        if (VIDEO_START > 1 or PAGE_START > 1):
            f = open(working_path + os.path.sep + 'snh48live.csv', 'at')
            port_csv = csv.writer(f)
        else:
            f = open(working_path + os.path.sep + 'snh48live.csv', 'wt')
            port_csv = csv.writer(f)
            port_csv.writerow(['title','info','url','m3u8_url'])

        # 获取每页视频
        video_list = []
        for i in range(PAGE_START,num+1):
            print("开始解析第%d页" % i)
            page_url = site_url + '/index/index/p/' + str(i) + '.html'
            r = requests.get(page_url, headers=HEADER)
            page_html = etree.HTML(r.text)

            page_list = page_html.xpath('//li[@class="videos"]')

            if VIDEO_START > len(page_list):
                print("VIDEO_START %d 超出范围(共%d页)" % (VIDEO_START,len(page_list)))
                sys.exit(1)

            if M3U8 == '1':
                if not os.path.isdir(working_path + os.path.sep + 'M3U8' + os.path.sep + RESOLUTION):
                    os.makedirs(working_path + os.path.sep + 'M3U8' + os.path.sep + RESOLUTION)

            index = 1
            for video in page_list:
                if ( (i == PAGE_START) and (index < VIDEO_START)):
                    index += 1
                    continue
                progressbar(index,len(page_list),"第%d页 第%d视频" % (i,index))
                video_img = video.xpath('.//img/@src')[0]
                video_url = site_url + video.xpath('.//a/@href')[0]
                parsed = _get_downloadable_from_url(video_url, RESOLUTION)

                if bool(parsed):
                    video_obj = snh48_video()
                    video_obj.update(parsed)
                    video_obj.addimgurl(video_img)
                    video_list.append(video_obj)

                    port_csv.writerow([video_obj.title, video_obj.info, video_obj.site_url,video_obj.m3u8_url])


                    if M3U8 == '1':
                        video_obj.write_tslist(working_path + os.path.sep + 'M3U8' + os.path.sep + RESOLUTION)

                    if DOWNLOAD == '1':
                        if not os.path.isdir(working_path):
                            os.makedirs(working_path)

                        video_obj.download(working_path)
                index += 1
        f.close()


if __name__ == '__main__':
    spider_snhLive()
