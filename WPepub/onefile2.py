#!/usr/bin/env python

### utils
from bs4 import BeautifulSoup
from collections import namedtuple
from config import options
from unidecode import unidecode
import os
import re
import requests
import subprocess
import tempfile

Chapter = namedtuple('Chapter', ['title', 'path', 'url', 'content'])

def html2rst(html):
    # adapted from http://johnpaulett.com/2009/10/15/html-to-restructured-text-in-python-using-pandoc/
    p = subprocess.Popen(['pandoc', '-S', '--from=html', '--wrap=none', '--to=rst'],
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
            mirror_path = os.path.join('mirror', result, 'index.html')
            mirror_path = unidecode(mirror_path.decode('utf-8'))
            chapters.append(Chapter(li.a.contents[0], mirror_path, url, ''))

    return chapters

def get_chapters2():
    http_matcher = re.compile('https?://.+\.com/(.*)')
    page_content = subprocess.check_output(['curl', '-s', options['toc_url']])
    soup = BeautifulSoup(page_content, 'html.parser')
    chapters = []
    for c in [x for x in soup.select('div.entry-content a') if 'class' not in x.attrs]:
        url = c.get('href')
        result = http_matcher.search(url).groups()[0]
        mirror_path = os.path.join('mirror', result, 'index.html')
        mirror_path = unidecode(mirror_path.decode('utf-8'))
        chapters.append(Chapter(c.contents[0], mirror_path, url, ''))

    return chapters


#
# workflow:
# 1. gather metadata
# 2. scrape files into mirror
# 3. convert files into rst
# 4. call txt2epub

def gather_metadata():
    url = options['first_chapter_url']
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    title = soup.head.title.text.encode('ascii', 'ignore')
    #soup.find(id='site-title').text
    base_url = re.search('(https?://.+\.com)/(.*)', url).groups()[0]

    return title, base_url

### scrape

def scrape():
    for chap in get_chapters2():
        os.system('mkdir -p ' + os.path.split(chap.path)[0])
        try:
            os.stat(chap.path)
        except Exception:
            continue
        with open(chap.path, 'w') as f:
            print "Scraping chapter %s" % chap.title
            f.write(subprocess.check_output(['curl', '-s', chap.url]))

### convert

def convert():
    chapters = []
    for chap in get_chapters2():
        print "converting chapter %s" % chap.path
        with open(chap.path, 'r') as f:
            content = BeautifulSoup(f.read(), 'html.parser')
        chapters.append(Chapter(title=chap.title, path=chap.path, url=chap.url, content=content))

    try:
        os.mkdir('rst')
    except OSError:
        pass

    for c in chapters:
        try:
            display_title = c.content.find_all(attrs={'class':'entry-title'})[0].get_text().encode('ascii', 'ignore')
        except Exception:
            display_title = "Undefined"
        fname = c.title + ' ' + display_title
        fname = fname.replace(' ', '_').replace('/', '-')
        if len(fname.split('.')[0]) == 1:
            fname = '0' + fname
        chapter_num = '%03d' % (chapters.index(c) + 1)
        fname = fname.encode('utf-8').decode('ascii', 'ignore')
        full_filename = 'rst/' + chapter_num + '-' + fname + '.rst'
        #if os.stat(full_filename): continue
        with open(full_filename, 'w') as f:
            f.write("{}\n{}\n".format(display_title,'='*(len(display_title))))
            text = html2rst(str(c.content.find_all("div", attrs={'class':'entry-content'})[0]))
            text = '\n'.join(text.splitlines()[1:-1])
            f.write(text)

def build_epub():
    with open('rst/1900-01-01-title-page.rst', 'w') as fh:
        title, base_url = gather_metadata()
        underline = "=" * len(title)
        fh.write(title + "\n" + underline + "\n")

    # call txt2epub
    try:
        os.mkdir('build')
    except OSError:
        pass

    cmd = ['txt2epub', 'build/out.epub', 'rst/*.rst', '--title="%s"' % title, '--creator=%s' % base_url]
    print cmd
    print ' '.join(cmd)
    p = subprocess.Popen(' '.join(cmd), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)



if __name__ == '__main__':
    print "Gathering metadata..."
    title, base_url = gather_metadata()
    print "Getting chapter list..."
    chapter_urls = get_chapters2()
    print chapter_urls
    try:
        os.mkdir('rst')
    except OSError:
        pass

    for chap in chapter_urls[0:4]:
        print "Processing chapter %s" % chap.title
        matches = re.search('(https?://.+\.com)/(.*)', chap.url)
        rst_filename = 'rst/%s.rst' % matches.groups()[1].replace('/', '-').strip('-')
        try:
            os.stat(rst_filename)
            continue
        except Exception:
            pass

        body = requests.get(chap.url).text
        print "Scraping chapter %s" % chap.title
        content = BeautifulSoup(body, 'html.parser')
        [s.extract() for s in content('script')]
        [s.extract() for s in content(class_='wpcnt')]
        [s.extract() for s in content(class_='sharedaddy')]

        try:
            display_title = content.find_all(attrs={'class':'entry-title'})[0].get_text().encode('ascii', 'ignore')
        except Exception:
            display_title = "Undefined"
        title = content.head.title.text.encode('ascii', 'ignore')
        fname = title + ' ' + display_title
        fname = fname.replace(' ', '_').replace('/', '-')
        if len(fname.split('.')[0]) == 1:
            fname = '0' + fname
        chapter_num = '%03d' % (chapter_urls.index(chap) + 1)
        fname = fname.encode('utf-8').decode('ascii', 'ignore')
        full_filename = 'rst/' + chapter_num + '-' + fname + '.rst'
        #if os.stat(full_filename): continue
        #with open(full_filename, 'w') as f:
        with open(rst_filename, 'w') as f:
            f.write("{}\n{}\n".format(display_title,'='*(len(display_title))))

            text = html2rst(str(content.find_all("div", attrs={'class':'entry-content'})[0]))
            text = text.replace('.. raw:: html', '')
            text = '\n'.join(text.splitlines()[1:-2])

            f.write(text)

    print "Done! Building epub"

    build_epub()
