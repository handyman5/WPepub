import os
import re
import subprocess
from bs4 import BeautifulSoup
from config import options
from unidecode import unidecode
from utils import html2rst, Chapter, get_chapters

def WP_scrape():
    chapters = []
    for chap in get_chapters():
        os.system('mkdir -p ' + os.path.split(chap.path)[0])
        with open(chap.path, 'w') as f:
            print "Scraping chapter %s" % chap.title
            f.write(subprocess.check_output(['curl', '-s', chap.url]))

if __name__ == '__main__':
    WP_scrape()
