import requests
import os
import sys
import time
from tqdm import tqdm
from bs4 import BeautifulSoup
from pypinyin import pinyin, lazy_pinyin
import json

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
    if not texts:
        return []
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

def createUrl3word(server, book_name):
    pinyin = ''.join(lazy_pinyin(book_name[0:3]))
    return '{0}/{1}/'.format(server, pinyin)

def createUrlLast3word(server, book_name):
    idx = book_name.index('.')
    pinyin = ''.join(lazy_pinyin(book_name[0:idx][-3:]))
    return '{0}/{1}/'.format(server, pinyin)

global book_names
with open("book_names.json", 'r', encoding='utf-8') as f:
    book_names = json.loads(f.read())

def createUrlFromJson(server, book_name):
    name = book_name[0:(book_name.index('.'))]
    if name in book_names:
        return '{0}/{1}/'.format(server, book_names[name])
    return creatUrlFullword(server, book_name)

def createUrlStrategy(createFunc, server, book_name):
    return createFunc(server, book_name)

def scratchFile(server, book_name, delOld=False):
    strategies = [createUrlFromJson, creatUrl2word, creatUrlFullword, createUrl3word, createUrlLast3word]
    while True:
        if len(strategies) == 0:
            raise Exception("No valid name found for {0}".format(book_name))
            break
        func = strategies.pop(0)
        target = createUrlStrategy(func, server, book_name)
        req = requests.get(url=target)
        req.encoding = 'utf-8'
        html = req.text
        # print('TESTING___',func, target, '\n')
        chapter_bs = BeautifulSoup(html, 'lxml')
        if testPage(chapter_bs):
            break
        # print('TESTING___',func, target, '\n')
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
        # print(chapter_name, url, '\n')
        content = get_content(url)
        with open(book_name, 'a', encoding='utf-8') as f:
            f.write(chapter_name)
            f.write('\n')
            f.write('\n'.join(content))
            f.write('\n')

def getMainPageBooks():
    server = 'https://www.kunnu.com'
    req = requests.get(url=server)
    bs = BeautifulSoup(req.text, 'lxml')
    chapters = bs.find('div', id='content')
    chapters = chapters.find_all('a', target='_blank')
    # titles = map(lambda c: c.get('title'), chapters)
    titles = []
    for c in chapters:
        titles.append(c.get('title'))
    return set(titles)

result_file = "result.txt"

def checkFinish(book_name):
    with open(result_file, 'r', encoding='utf-8') as f:
        results = f.read()
        if results.find(book_name) >= 0:
            return True
    return False
def finishBook(book_name):
    with open(result_file, 'a', encoding='utf-8') as f:
        f.write('\n')
        f.write(book_name)

if __name__ == '__main__':
    server = 'https://www.kunnu.com'
    book_name = '白夜行.txt'
    if len(sys.argv) >= 2:
        book_name = '{0}.txt'.format(sys.argv[1])
    books = getMainPageBooks()
    for book_name in books:
        if checkFinish(book_name):
            continue
        full_book_name = f'{book_name}.txt'
        try:
            print("Start scratch book", book_name)
            scratchFile(server, full_book_name, True)
            print("Success !!!!!!!! ", book_name, "download finish.")
            finishBook(book_name)
        except:
            print("Exception for", book_name, sys.exc_info()[0].args)

    print("Download all done.")

