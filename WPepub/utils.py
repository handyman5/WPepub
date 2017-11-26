from bs4 import BeautifulSoup
from collections import namedtuple
from config import options
from unidecode import unidecode
import os
import re
import subprocess

Chapter = namedtuple('Chapter', ['title', 'path', 'url', 'content'])

def html2rst(html):
    # adapted from http://johnpaulett.com/2009/10/15/html-to-restructured-text-in-python-using-pandoc/
    p = subprocess.Popen(['pandoc', '--from=html', '--no-wrap', '--to=rst'],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    return unidecode(p.communicate(html)[0].decode('utf-8'))

def get_chapters():
    # Pull down a single episode in order to extract the TOC
    page_content = subprocess.check_output(['curl', '-s', options['first_chapter_url']])
    soup = BeautifulSoup(page_content, 'html.parser')
    categories = soup.find_all(attrs={"class":options['categories_selector']})[0]
    groups = categories.contents[2]

    lis = groups.find_all("li")
    chapters = []
    http_matcher = re.compile('https?://.+\.com/(.*)')
    for li in lis:
        if li.li is None:
            print li.a.contents[0], li.a.get('href')
            url = li.a.get('href')
            result = http_matcher.search(url).groups()[0]
            mirror_path = os.path.join('../mirror', result, 'index.html')
            ##mirror_path = os.path.join(url.replace('https://parahumans.wordpress.com', '../mirror'),'index.html')
            #mirror_path = os.path.join(url.replace('https://practicalguidetoevil.wordpress.com', '../mirror'),'index.html')
            mirror_path = unidecode(mirror_path.decode('utf-8'))
            chapters.append(Chapter(li.a.contents[0], mirror_path, url, ''))

    return chapters
