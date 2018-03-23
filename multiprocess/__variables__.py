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
RECONNECTION_TIME = 1

# MENU VARIABLES/菜单项变量
RESOLUTION = 'liuchang' # video resolution/清晰度

# HTTP REQUESTS VARIABLES/HTTP REQUESTS变量
MAIN_PAGE_API = '/index/index/p/%s.html'
TRIALLIMIT_PER_PAGE = 10

# HTTP DEBUG INFO/HTTP 诊断信息
ERROR_STATUS_CODE = "Invalid status_code from %s: %s"
ERROR_CONNECTION_TIMEOUT = "Unable to connect to %s after %s seconds."
ERROR_CONNECTION_TRIALLIMIT = "Unable to connect to %s after %s trial times"
