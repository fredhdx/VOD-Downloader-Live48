# SYSTEM VARIABLES/系统变量

HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) \
    AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/35.0.1916.114 Safari/537.36'
    }

DOMAIN = {
    'SNH48': "http://live.snh48.com",
    'GNZ48': "http://live.gnz48.com",
    'BEJ48': "http://live.bej48.com",
    'SHY48': "http://live.shy48.com",
    'CKG48': "http://live.ckg48.com"
    }

GREENLET_SIZE = 100
CONNECTION_TIMEOUT = 90

# MENU VARIABLES/菜单项变量

DOWNLOAD = '0' # Single video/单个视频
SHOW = '0'   #
MERGE_TS = '0' # merge downloaded .ts/合并ts文件
SINGLE_CONTINUE = '0' # continue download existing video/断点续传
RE_DOWNLOAD = '0' # erase and re-download existing video/重新下载
DOWNLOAD = '1' # download/是否下载
RESOLUTION = 'chaoqing' # video resolution/清晰度

# HTTP REQUESTS VARIABLES/HTTP REQUESTS变量
MAIN_PAGE_API = '/index/index/p/%s.html'
TRIALLIMIT_PER_PAGE = 10

# DEBUG/诊断
ERROR_STATUS_CODE = "Requests error, status_code: %s"
ERROR_CONNECTION_TIMEOUT = "Unable to connect to %s after %s seconds of ConnectionErrors"
ERROR_CONNECTION_TRIALLIMIT = "Unable to connect to %s after %s trial times"
