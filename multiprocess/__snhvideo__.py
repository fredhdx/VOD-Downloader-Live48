# 对象定义
import logging
import os
import shutil
import time
import traceback
import requests
from __utilities__ import press_to_exit
from __utilities__ import progressbar
from __variables__ import CONNECTION_TIMEOUT

logger = logging.getLogger(__name__)

class Snh48Video:
    """ A SNH48 Video class
            Store, write and download
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
            logger.info("Error: snh48_video.update(args): empty args")
            press_to_exit()
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
                    logger.info("Warning: key %s not found in snh48_video", k_args)

    def addimgurl(self, imgurl):
        """ Add imgurl to class.
        """
        if not imgurl:
            self.img_url = imgurl

    def write_tslist(self, path):
        """ Write video ts list to text file
        """
        if not path:
            logger.info("Error: snh48_video.write_tslist(path): empty path")
            press_to_exit()
        else:
            path = path + os.path.sep + self.fname + '.m3u8'

        try:
            f = open(path, 'wt')
        except OSError as e:
            logger.info(e)
            traceback.print_exc()
            press_to_exit()

        if not self.ts_list:
            logger.info("Error: empty ts_list for %s %s", self.title, self.info)
        else:
            for line in self.ts_list:
                f.write(line['ts_url'] + '\n')
        f.close()

    def download(self, path, RESOLUTION='liuchang'):
        """ Downlaod video to path, with resolution RESOLUTION (default: liuchang/流畅)
                Warning: RESOLUTION is set by wrapper functions. If used separately,
                please specify; otherwise the lowest quality is used.
        """
        if not path:
            logger.info("Error: snh48_video.download(path): empty path")
            press_to_exit()
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

            # write ts list: ts list is saved to file to enable continue/re-download function
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
                        logger.info("\nsnh48_video.download: write_ts: connection error")
                        press_to_exit()

                tsNames.append(tmp_name)
                index += 1

            logger.info('All .ts files downloaded for: ' + self.fname)

            if index == len(self.ts_list) + 1:
                with open(path + os.path.sep + self.fname, 'wb') as f:
                    for ts in tsNames:
                        with open(ts, 'rb') as mergefile:
                            shutil.copyfileobj(mergefile, f)
                        os.remove(ts)
                    logger.info('%s merged', self.fname)
            else:
                logger.info('Merge failed for %s', self.fname)
