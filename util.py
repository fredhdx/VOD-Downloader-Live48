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
    text = text.replace(u'\uff61', ' ')
    # White space
    text = text.replace(u'\t', ' ').replace(u'\r', ' ')

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
