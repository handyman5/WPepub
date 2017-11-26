import os
from bs4 import BeautifulSoup
from unidecode import unidecode
from utils import html2rst, Chapter

def WP_convert():
    # Pull down a single episode in order to extract the TOC
    #with open("../mirror/category/stories-arcs-1-10/arc-1-gestation/1-01/index.html", 'r') as f:
    with open("../mirror/2017/09/04/chapter-28-gambits/index.html", 'r') as f:

        page_content = f.read()

    soup = BeautifulSoup(page_content, 'html.parser')

    categories = soup.find_all(attrs={"class":"menu-item-1416"})[0]
    #categories = soup.find_all(attrs={"class":"widget_categories"})[0]
    groups = categories.contents[2]

    lis = groups.find_all("li")
    chapters = []
    for li in lis:
        if li.li is None:
            print li.a.contents[0], li.a.get('href')
            url = li.a.get('href')
            mirror_path = os.path.join(url.replace('https://practicalguidetoevil.wordpress.com', '../mirror'), 'index.html')
            #mirror_path = os.path.join(url.replace('https://parahumans.wordpress.com', '../mirror'), 'index.html')
            mirror_path = unidecode(mirror_path.decode('utf-8'))
            if 'arc-29' in mirror_path:
                break
            with open(mirror_path, 'r') as f:
                content = BeautifulSoup(f.read(), 'html.parser')
            chapters.append(Chapter(title=li.a.contents[0], url=url, content=content))

    try:
        os.mkdir('../rst')
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
        chapter_num = '%03d' % chapters.index(c)
        fname = fname.encode('utf-8').decode('ascii', 'ignore')
        f = open('../rst/' + chapter_num + '-' + fname + '.rst', 'w')
        f.write("{}\n{}\n".format(display_title,'='*(len(display_title))))
        text = html2rst(str(c.content.find_all("div", attrs={'class':'entry-content'})[0]))
        text = '\n'.join(text.splitlines()[1:-1])
        f.write(text)
        f.close()

if __name__ == '__main__':
    WP_convert()
