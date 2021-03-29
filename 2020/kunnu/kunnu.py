import requests
import os
import sys
import time
from tqdm import tqdm
from bs4 import BeautifulSoup
from pypinyin import pinyin, lazy_pinyin

"""
    Author:
        Zhang Cheng
    鲲弩小说
"""

def get_content(target):
    req = requests.get(url = target)
    req.encoding = 'utf-8'
    html = req.text
    bf = BeautifulSoup(html, 'lxml')
    texts = bf.find('div', id='nr1')
    texts = texts.find_all('p')

    content = map(lambda i : i.text, texts)
    return content

def testPage(bs):
    error = bs.text
    if error.find('Error 404') >= 0 :
        return False
    return True

def creatUrl2word(server, book_name):
    pinyin = ''.join(lazy_pinyin(book_name[0:2]))
    return '{0}/{1}/'.format(server, pinyin)

def creatUrlFullword(server, book_name):
    idx = book_name.index('.')
    pinyin = ''.join(lazy_pinyin(book_name[0:idx]))
    return '{0}/{1}/'.format(server, pinyin)

def createUrlStrategy(createFunc, server, book_name):
    return createFunc(server, book_name)

def scratchFile(server, book_name, delOld=False):
    strategies = [creatUrl2word, creatUrlFullword]
    while True:
        if len(strategies) == 0:
            break
        func = strategies.pop(0)
        target = createUrlStrategy(func, server, book_name)
        req = requests.get(url=target)
        req.encoding = 'utf-8'
        html = req.text
        print('TESTING___',func, target, '\n')
        chapter_bs = BeautifulSoup(html, 'lxml')
        if testPage(chapter_bs):
            break

    chapters = chapter_bs.find('div', id='content-list')
    chapters = chapters.find_all('a', target='_blank')
    first = chapters.pop(0)
    chapters.append(first)
    visited = []
    if delOld:
        if os.path.exists(book_name):
            os.remove(book_name)
    for chapter in tqdm(chapters):
        chapter_name = chapter.string
        url = chapter.get('href')
        if url in visited:
            continue
        visited.append(url)
        print(chapter_name, url, '\n')
        content = get_content(url)
        with open(book_name, 'a', encoding='utf-8') as f:
            f.write(chapter_name)
            f.write('\n')
            f.write('\n'.join(content))
            f.write('\n')

if __name__ == '__main__':
    server = 'https://www.kunnu.com'
    book_name = '白夜行.txt'
    if len(sys.argv) >= 2:
        book_name = '{0}.txt'.format(sys.argv[1])
    scratchFile(server, book_name, True)
