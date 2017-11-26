import os
from bs4 import BeautifulSoup
from unidecode import unidecode
from utils import html2rst, Chapter, get_chapters

def WP_convert():
    chapters = []
    for chap in get_chapters():
        with open(chap.path, 'r') as f:
            content = BeautifulSoup(f.read(), 'html.parser')
        chapters.append(Chapter(title=chap.title, path=chap.path, url=chap.url, content=content))

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
