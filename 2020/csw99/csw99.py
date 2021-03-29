import requests
import os
import time
from tqdm import tqdm
from bs4 import BeautifulSoup

"""
    Author:
        Zhang Cheng
    99藏书网
"""

def get_content(target):
    req = requests.get(url = target)
    req.encoding = 'utf-8'
    html = req.text
    print(target)
    print(html)
    bf = BeautifulSoup(html, 'lxml')
    texts = bf.find('div', id='content')
    print(texts.text)
    texts = texts.find_all('div')
    for t in texts:
        print(t.text)
        time.sleep(0.5)

    content = map(lambda i : i.text, texts)
    return content

def scratchFile(book_name, delOld=False):
    server = 'https://www.99csw.com'
    target = 'https://www.99csw.com/book/2910/index.htm'
    req = requests.get(url = target)
    req.encoding = 'utf-8'
    html = req.text
    chapter_bs = BeautifulSoup(html, 'lxml')
    chapters = chapter_bs.find('dl', id='dir')
    chapters = chapters.find_all('a')
    if delOld:
        if os.path.exists(book_name):
            os.remove(book_name)
    for chapter in tqdm(chapters):
        chapter_name = chapter.string
        url = server + chapter.get('href')
        content = get_content(url)
        print(url)
        with open(book_name, 'a', encoding='utf-8') as f:
            f.write(chapter_name)
            f.write('\n')
            f.write('\n'.join(content))
            f.write('\n')
        break

if __name__ == '__main__':
    server = 'https://www.99csw.com'
    book_name = '白夜行.txt'
    scratchFile(book_name, True)
