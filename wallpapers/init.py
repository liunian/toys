#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import bs4
import re
import os
import sys
from multiprocessing import Pool, cpu_count
try:
    import urlparse
    from urllib import urlencode
except: # For Python 3
    import urllib.parse as urlparse
    from urllib.parse import urlencode

api = 'https://wall.alphacoders.com/search.php?min_resolution=1920x1080&sort_search=rating'
keyword = 'anime+girl'
start_page = 1
end_page = 10
dest = os.path.expanduser('~/Pictures/wallpapers/')

block_list_file = os.path.join(dest, '.block.txt')
block_files = []
try:
    block_files = open(block_list_file, 'r').readlines()
except:
    open(block_list_file, 'w')

def not_none(link):
    return link is not None

def is_blocked(filename):
    return filename in block_files

def get_page_pics(page):
    """
    get list of pics in special page
    """
    url_parts = list(urlparse.urlparse(api))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update({'search': keyword, 'page': page})
    url_parts[4] = urlencode(query)
    url = urlparse.urlunparse(url_parts)
    # url = api + '?search=' + keyword + "&page=" + str(page)
    print url
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    imgs = [ele.attrs.get('data-href') for ele in soup.select('.boxcaption .download-button')]
    imgs = filter(not_none, imgs)
    return imgs

def gen_filename(src):
    if not src:
        return None

    ptn = re.compile(r'/wallpaper/(\d+)/.+?/([a-zA-Z]+)/')
    groups = ptn.findall(src)

    if len(groups) != 1 or len(groups[0]) != 2:
        return None

    return groups[0][0] + '.' + groups[0][1]

def download_pic(img):
    filename = gen_filename(img)

    if is_blocked(filename):
        print '\t' + filename + ' had been blocked'
        return

    filepath = os.path.join(dest, filename)
    if not os.path.exists(filepath):
        print '\tdownload ' + img
        img_data = requests.get(img)
        open(filepath, 'wb').write(img_data.content)
    else:
        print '\texist ' + filepath

def crawl():
    for i in list(range(start_page, end_page + 1)):
        print 'analysics page ' + str(i)
        imgs = get_page_pics(i)
        pool = Pool(cpu_count())
        pool.map(download_pic, imgs)
    print 'Done'

def run():
    crawl()
    pass

run()
