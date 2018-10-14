#!/usr/bin/env python

from argparse import ArgumentParser
from bs4 import BeautifulSoup
from unidecode import unidecode
import os
import re
import requests
import subprocess
import sys
import yaml

def html2rst(html):
    # adapted from http://johnpaulett.com/2009/10/15/html-to-restructured-text-in-python-using-pandoc/
    p = subprocess.Popen(['pandoc', '--from=html+smart', '--wrap=none', '--to=rst+smart'],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    return unidecode(p.communicate(html)[0].decode('utf-8'))

def get_chapters(options):
    if 'toc_parser' in options:
        page_content = requests.get(options['toc_url'], headers={'User-Agent': 'curl/7.54.0'}).text
        soup = BeautifulSoup(page_content, 'html.parser')
        chapters = eval(options['toc_parser'].strip())
    if 'url_list' in options:
        chapters = options['url_list']
    return chapters

def write_chapter(chap, index, filename, options):
    print "Processing chapter %s" % chap

    try:
        os.mkdir('rst-%s' % filename)
    except OSError:
        pass

    matches = re.search('(https?://.+\.com)/(.*)', chap)
    rst_filename = 'rst-%s/%03d.%s.rst' % (filename, index + 1, unidecode(matches.groups()[1].replace('/', '-').strip('-')))
    try:
        # skip if we've already processed this one
        os.stat(rst_filename)
        return
    except Exception:
        pass

    body = requests.get(chap, headers={'User-Agent': 'curl/7.54.0'}).text
    content = BeautifulSoup(body, 'html.parser')
    [s.extract() for s in content('script')]
    [s.extract() for s in content(class_='wpcnt')]
    [s.extract() for s in content(class_='sharedaddy')]
    [s.extract() for s in content('br')]
    [s.extract() for s in content('img')]
    [s.extract() for s in content('hr')]
    [s.extract() for s in content(text=u'\u2619')]
    
    try:
        display_title = content.find_all(attrs={'class':options.get('title_class')})[0].get_text().encode('ascii', 'ignore')
    except Exception:
        display_title = "Undefined"

    with open(rst_filename, 'w') as f:
        f.write("{}\n{}\n".format(display_title,'='*(len(display_title))))
        text = html2rst(str(content.find_all("div", attrs={'class':options.get('content_class')})[0]))
        text = text.replace('.. raw:: html', '')
        text = '\n'.join(text.splitlines()[1:])
        f.write(text)

def build_epub(url, filename):
    with open('rst-%s/000.title-page.rst' % filename, 'w') as fh:
        soup = BeautifulSoup(requests.get(url, headers={'User-Agent': 'curl/7.54.0'}).text, 'html.parser')
        title = soup.head.title.text.encode('ascii', 'ignore')
        base_url = re.search('(https?://.+\.com)/(.*)', url).groups()[0]
        underline = "=" * len(title)
        fh.write(title + "\n" + underline + "\n")

    try:
        os.mkdir('build')
    except OSError:
        pass

    cmd = ['txt2epub', 'build/%s.epub' % filename, 'rst-%s/*.rst' % filename, '--title="%s"' % title, '--creator=%s' % base_url]
    p = subprocess.Popen(' '.join(cmd), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    p.communicate()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-c', '--config', help='YAML config file to use')
    args = parser.parse_args()
    if not args.config:
        print "Specify 'toc_url' and 'toc_parser' in a YAML file, or a list of URLs named 'url_list'"
        sys.exit(2)

    options = yaml.load(open(args.config))
    filename = args.config.replace('.yaml', '')
    chapter_urls = get_chapters(options)
    for chap in chapter_urls:
        write_chapter(chap, chapter_urls.index(chap), filename, options)
    build_epub(options['toc_url'], filename)
