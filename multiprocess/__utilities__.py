#!/usr/bin/python3
# coding:utf-8 #
""" 字符串处理
"""
import logging
import os
import platform
import re
import sys
import time


def legitimize(text, myos=platform.system()):
    """Converts a string to a valid filename.
       credit: soimort/you-get.
       option: filename.
    """
    # POSIX systems
    text = text.translate({
        0: None,
        ord('/'): '-',
        ord('|'): '-',
        ord(':'): '-',
        ord('\uFF1A'): ' ',
    })

    if  myos == 'Windows':
        # Windows (non-POSIX namespace)
        text = text.translate({
            # Reserved in Windows VFAT and NTFS
            ord(':'): '-',
            ord('\uFF1A'): ' ',
            ord('*'): '-',
            ord('?'): '-',
            ord('\\'): '-',
            ord('\"'): '\'',
            # Reserved in Windows VFAT
            ord('+'): '-',
            ord('<'): '-',
            ord('>'): '-',
            ord('['): '(',
            ord(']'): ')',
        })
    else:
        # *nix
        if myos == 'Darwin':
            # Mac OS HFS+
            text = text.translate({
                ord(':'): '-',
            })

        # Remove leading .
        if text.startswith("."):
            text = text[1:]

    text = text[:80] # Trim to 82 Unicode characters long
    return text

def remove_nbws(text):
    """ remove unwanted unicode punctuation: zwsp, nbws, \t, \r, \r.
    """

    # ZWSP: Zero width space
    text = text.replace(u'\u200B', '')
    # NBWS: Non-breaking space
    text = text.replace(u'\xa0', ' ')
    # HalfWidth fullstop
    text = text.replace(u'\uff61', '')
    # Bullet
    text = text.replace(u'\u2022', '')
    # White space
    text = text.replace(u'\t', ' ').replace(u'\r', ' ')

    # General Punctuation
    gpc_pattern = re.compile(r'[\u2000-\u206F]')
    text = gpc_pattern.sub('', text)

    # Mathematical Operator
    mop_pattern = re.compile(r'[\u2200-\u22FF]')
    text = mop_pattern.sub('', text)

    # Combining Diacritical Marks
    dcm_pattern = re.compile(r'[\u0300-\u036F]')
    text = dcm_pattern.sub('', text)

    lsp_pattern = re.compile(r'[\x80-\xFF]')
    text = lsp_pattern.sub('', text)

    return text

def remove_extended(text):
    """ remove Chinese punctuation and Latin Supplement.
        https://en.wikipedia.org/wiki/Latin-1_Supplement_(Unicode_block)
    """

    # latin supplement: \u00A0-\u00FF
    # notice: nbsp is removed here
    lsp_pattern = re.compile(r'[\x80-\xFF]')
    text = lsp_pattern.sub('', text)

    # chinese special character
    # chc_pattern = re.compile(r'[\r\t\n\.\!\/_,$%^*(+\"\')]|[+——()?【】“”！，。？、~@#￥%……&*（）]')
    # text = chc_pattern.sub('',text)

    return text

def oneliner(text):
    """ remove \n in text.
    """
    return text.replace(u'\n', ' ')

def crush_time(text):
    """ Extract and crush YYYY-MM-DD into YYYYMMDD.
        If not date string, return original string
    """

    date_string_search = re.search(r'\d{4}[\.|\-|:|\/]\d{2}[\.|\-|:|\/]\d{2}', text) # date pattern: YYYY[sep]MM[sep]DD
    if date_string_search:
        date_string = re.sub(r'[\.|\-|:|\/]','', date_string_search.group(0)) # convert date string: YYYYMMMDD
    else:
        date_string = text # if no date found, use info[:10] part

    return date_string

def clean_string(text, option):
    """ main string processing function.
        option: 'filename', 'content', 'content_oneliner', 'very_clean'
    """
    text = text.strip()
    if not text:
        return text

    if option == 'filename': # legitimize for used as filename Note: filename should not be a path!
        text = oneliner(text)
        text = remove_nbws(text)
        text = legitimize(text)
    elif option == 'content': # retain special characters in utf-8
        text = remove_nbws(text)
    elif option == 'content_oneliner':
        text = oneliner(text)
        text = remove_nbws(text)
    elif option == 'very_clean':
        text = remove_nbws(text)
        text = remove_extended(text)

    return text

def compare_to_search_keywords(search_pattern, target_string):
    ''' compare search_pattern and SnhVideo object's fname. Return a boolean.
    '''
    search_pattern = search_pattern.lower()
    target_string = target_string.lower()

    MATCH = False
    search_pattern_options = search_pattern.split(',')
    for each_option in search_pattern_options:

        words = each_option.strip().split('+')
        SUB_MATCH = True
        for word in words:
            if word == 'team x':
                target_string = target_string.replace('team xii', '')

            SUB_MATCH = SUB_MATCH and (word.strip() in target_string)

        MATCH = MATCH or SUB_MATCH

    return MATCH

def press_to_exit():
    logger = logging.getLogger()
    input("\n按任意键退出")

    logger.info("再见 Bye!")
    sys.exit()

def timefunc(f):
    '''
    Time profiling function adapted from "Simple Timers" example at
    https://zapier.com/engineering/profiling-python-boss/
    '''
    def f_timer(*args, **kwargs):
        start = time.time()
        result = f(*args, **kwargs)
        end = time.time()
        elapsed_time = end - start
        #print(f.__name__ + ' took ' + str(elapsed_time) + ' seconds')
        return (result, elapsed_time)
    return f_timer

def combineTitles(title, info):
    ''' process title and info > fname
    '''

    fname = title
    if not fname.startswith("《"):
        fname = "《" + fname + "》"

    date_string = crush_time(info)[:10] # if no date found, use title2[:10] part
    fname = date_string + ' ' + fname # 《48狼人杀》 20180202

    if "星梦Mini" in fname:
        fname = fname + ' ' + re.sub('本期成员：', '', re.search(r'.*' + date_string[:4], info).group(0)[:-4])
    if "48狼人杀" in fname or "公演" in fname:
        fname = fname + ' ' + re.search(r'.*' + date_string[:4], info).group(0)[:-4]

    fname = clean_string(title, 'filename')

    return fname

def progressbar(count, total, status=''):
    """ show progressbar/进度条
    """
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar_str = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar_str, percents, '%', status))
    sys.stdout.flush()

def setup_working_path(CREATE=False):
    ''' Set up working direcotry, always under the folder containg the script.
    '''
    logger = logging.getLogger()

    logger.info("--------------------------------------------------------------")
    logger.info("设置工作文件夹/Set up working path")
    choice = input("默认/deault: /snh48live: ")
    if not choice:
        working_path = os.getcwd() + '/snh48live'
    else:
        choice = choice[1:] if choice[0] == os.path.sep else choice
        working_path = os.getcwd() + os.path.sep + choice

    logger.info("工作文件夹: %s", working_path)

    if not os.path.isdir(working_path):
        _prompt = "工作文件夹不存在，是否创立: 1.是 2.否（默认）" + os.linesep + "Working path not existing. Create it? 1. Yes  2. No (default)"
        choice = input(_prompt)
        if choice == '1':
            os.makedirs(working_path)
        else:
            logger.info("开始下载前需要创立工作文件夹")
            return ''

    return working_path
