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
    p = subprocess.Popen(['pandoc', '-S', '--from=html', '--wrap=none', '--to=rst'],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    return unidecode(p.communicate(html)[0].decode('utf-8'))

def get_chapters(options):
    page_content = requests.get(options['toc_url']).text
    soup = BeautifulSoup(page_content, 'html.parser')
    if 'toc_parser' in options:
        chapters = [x.get('href') for x in eval(options['toc_parser'].strip())]
    else:
        chapters = [x.get('href') for x in soup.select('div.entry-content a') if 'class' not in x.attrs]
    return chapters

def write_chapter(chap, index):
    print "Processing chapter %s" % chap

    try:
        os.mkdir('rst')
    except OSError:
        pass

    matches = re.search('(https?://.+\.com)/(.*)', chap)
    rst_filename = 'rst/%03d.%s.rst' % (index + 1, matches.groups()[1].replace('/', '-').strip('-'))
    try:
        # skip if we've already processed this one
        os.stat(rst_filename)
        return
    except Exception:
        pass

    body = requests.get(chap).text
    print "Scraping chapter %s" % chap
    content = BeautifulSoup(body, 'html.parser')
    [s.extract() for s in content('script')]
    [s.extract() for s in content(class_='wpcnt')]
    [s.extract() for s in content(class_='sharedaddy')]

    try:
        display_title = content.find_all(attrs={'class':'entry-title'})[0].get_text().encode('ascii', 'ignore')
    except Exception:
        display_title = "Undefined"

    with open(rst_filename, 'w') as f:
        f.write("{}\n{}\n".format(display_title,'='*(len(display_title))))
        text = html2rst(str(content.find_all("div", attrs={'class':'entry-content'})[0]))
        text = text.replace('.. raw:: html', '')
        text = '\n'.join(text.splitlines()[1:-2])
        f.write(text)

def build_epub(url):
    with open('rst/000.title-page.rst', 'w') as fh:
        soup = BeautifulSoup(requests.get(url).text, 'html.parser')
        title = soup.head.title.text.encode('ascii', 'ignore')
        base_url = re.search('(https?://.+\.com)/(.*)', url).groups()[0]
        underline = "=" * len(title)
        fh.write(title + "\n" + underline + "\n")

    try:
        os.mkdir('build')
    except OSError:
        pass

    cmd = ['txt2epub', 'build/out.epub', 'rst/*.rst', '--title="%s"' % title, '--creator=%s' % base_url]
    p = subprocess.Popen(' '.join(cmd), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    p.communicate()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-c', '--config', help='YAML config file to use')
    args = parser.parse_args()
    if not args.config:
        print "Specify 'toc_url' and 'toc_parser' in a YAML file"
        sys.exit(2)

    options = yaml.load(open(args.config))
    chapter_urls = get_chapters(options)
    for chap in chapter_urls[0:4]:
        write_chapter(chap, chapter_urls.index(chap))
    build_epub(options['toc_url'])
