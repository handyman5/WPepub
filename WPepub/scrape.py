import subprocess
import os
from bs4 import BeautifulSoup
from unidecode import unidecode
from utils import html2rst, Chapter

def WP_scrape():
    # Pull down a single episode in order to extract the TOC
    page_content = subprocess.check_output(['curl', '-s',
                                            'https://practicalguidetoevil.wordpress.com/2015/03/25/prologue/'])

                                            #'https://parahumans.wordpress.com/category/stories-arcs-1-10/arc-4-shell/4-x-interlude/'])

    soup = BeautifulSoup(page_content, 'html.parser')

    #categories = soup.find_all(attrs={"class":"widget_categories"})[0]
    categories = soup.find_all(attrs={"class":"menu-item-1416"})[0]
    groups = categories.contents[2]

    lis = groups.find_all("li")
    chapters = []
    for li in lis:
        if li.li is None:
            print li.a.contents[0], li.a.get('href')
            url = li.a.get('href')
            #mirror_path = os.path.join(url.replace('https://parahumans.wordpress.com', '../mirror'),'index.html')
            mirror_path = os.path.join(url.replace('https://practicalguidetoevil.wordpress.com', '../mirror'),'index.html')
            mirror_path = unidecode(mirror_path.decode('utf-8'))
            os.system('mkdir -p ' + os.path.split(mirror_path)[0])
            with open(mirror_path, 'w') as f:
                f.write(subprocess.check_output(['curl', '-s', url]))

if __name__ == '__main__':
    WP_scrape()
