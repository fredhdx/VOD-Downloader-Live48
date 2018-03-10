import gevent.pool as pool
import gevent.monkey
gevent.monkey.patch_all()

import requests

def make_requests(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return 1
        else:
            return 0
    except requests.ConnectionError:
        return -1

def foo(url):
    p = pool.Pool(3)
    subRec = p.map(make_requests, [url] * 3)

    return subRec

def run():

    url = "http://www.google.com"

    p = pool.Pool(100)
    records = p.map(foo, [url] * 100)
    return records
