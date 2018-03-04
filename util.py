#!/usr/bin/python3
# coding:utf-8 #
""" 字符串处理
"""

import platform
import re

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


def search_by_keywords(search_pattern, target_string):
    ''' 回车选择所有视频, 不同关键字通过,分割，必要条件通过+添加
        例子1：Team NII + 公演 搜索 含有Team NII和公演关键字的视频
        例子2：剧场女神 + Team X, 梦想的旗帜 + Team X 搜索 Team X名下剧场女神或旗帜两场公演的视频
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