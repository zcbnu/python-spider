import os
import re
import json
import requests
from BookPathGuess import BookPathGuess
from bs4 import BeautifulSoup, NavigableString
from tqdm import tqdm


class BookSite:

    def __init__(self, js='', file='', download=False, debug=False):
        '''
        Args:
            js: should be json format string or a json object, describe how to scratch a website.
            file: should be a json file
        '''
        if len(file) > 0:
            with open(file, 'r', encoding='utf-8') as f:
                js = f.read()
        if isinstance(js, str):
            js = json.loads(js)
        self.json = js
        self.templateLoaded = False
        self.debug = debug
        self.templateJson = {}
        self.downloadFile = download

    def get(self, key):
        if key not in self.json:
            self.try_load_template()
            if key not in self.templateJson:
                return None
                # raise Exception("Key {0} in BookSite has not support yet.".format(key))
            return self.templateJson[key]
        return self.json[key]

    def try_load_template(self):
        if not self.templateLoaded:
            self.templateLoaded = True
            with open("template.json", 'r', encoding='utf-8') as f:
                self.templateJson = json.loads(f.read())

    def _second_dir_elements(self, site):
        response_bs = BeautifulSoup(self.get_content_html(site), 'lxml')
        elements = self.get("second_dir_elements")
        results = []
        for element in elements:
            bs = response_bs.find_all(element['name'], element['attrs'])
            sub = element['sub']

            stack = bs
            while sub is not None:
                sub_stack = []
                while len(stack) > 0:
                    cur = stack.pop()
                    if "attrs" in sub:
                        children = cur.find_all(sub['name'], sub["attrs"])
                    else:
                        children = cur.find_all(sub['name'])
                    sub_stack = sub_stack + children
                stack = sub_stack
                if "sub" in sub:
                    sub = sub['sub']
                else:
                    sub = None
            results = results + stack
        return results

    def _guess_book_url(self, book_name):
        url = self.get("url")
        prefix_list = []
        if self.get("second_dir_elements") is not None:
            elements = self._second_dir_elements(url)
            for e in elements:
                prefix_list.append("{0}/{1}".format(url, e.get('href')))
        else:
            prefix_list.append(url)
        print("PrefixList:\n====", '\n===='.join(prefix_list))
        for guess in BookPathGuess(book_name):
            for prefix in prefix_list:
                target = "{0}/{1}/".format(prefix, guess)
                if self.debug:
                    print("Try ", target)
                try:
                    result = self.get_content_html(target)
                except:
                    result = self.get("failure_str")

                if self._check_book_index_page_valid(result):
                    if self.debug:
                        print("Guess path success. ", guess)
                    return result
                if self.debug:
                    print("Guess path failed. ", guess)
        return False

    def _check_book_index_page_valid(self, html):
        return html.find(self.get("failure_str")) < 0

    def get_chapter_bs(self, html, element_root_str, elements_str):
        base_chapter_bs = BeautifulSoup(html, 'lxml')
        index_elements = self.get(element_root_str)
        for element in index_elements:
            if "name" not in element:
                raise Exception("{0} format error. key 'name' no found in element {1}".format(element_root_str, element))
            name = element['name']
            if "id" in element:
                chapter_bs = base_chapter_bs.find(name, id=element["id"])
            elif "target" in element:
                chapter_bs = base_chapter_bs.find(name, target=element["target"])
            elif "attrs" in element:
                chapter_bs = base_chapter_bs.find(name, element["attrs"])
            else:
                chapter_bs = base_chapter_bs.find(name)
            if not chapter_bs:
                if self.debug:
                    print("Index element name:{0} not found. {1}".format(name, base_chapter_bs.text))
                return []
        chapter_element = self.get(elements_str)
        if "name" not in chapter_element:
            raise Exception("{0} format error. key 'name' no found in element {1}".format(elements_str, chapter_element))
        name = chapter_element["name"]
        if "id" in chapter_element:
            chapter_bs = chapter_bs.find_all(name, id=chapter_element["id"])
        elif "target" in chapter_element:
            chapter_bs = chapter_bs.find_all(name, target=chapter_element["target"])
        else:
            chapter_bs = chapter_bs.find_all(name)
        return chapter_bs

    def _sort_chapters(self, chapter_bs):
        if self.get("resort_chapter"):
            first = chapter_bs.pop(0)
            chapter_bs.append(first)
        return chapter_bs

    def _format_content(self, content):
        fm = self.get('content_format')
        if not fm:
            return content.text
        result = content.text
        if "replace" in fm:
            result = re.sub(fm["replace"][0], fm["replace"][1], content.text)
        return result

    def _join_content(self, content_bs):
        content = map(lambda i: self._format_content(i), content_bs)
        return self.get('delimiter').join(content)

    def _get_book_file_name(self, book_name):
        idx = str.find(book_name, '.')
        if idx < 0:
            return "{0}.txt".format(book_name)
        return book_name

    def scratch_book(self, book_name):
        if self.debug:
            print("Start scratch book.")
        html = self._guess_book_url(book_name)
        if not html:
            raise Exception("Cannot find valid book url for {0}".format(book_name))
        chapter_bs = self.get_chapter_bs(html, "chapter_root_element", "chapter_elements")
        chapter_bs = self._sort_chapters(chapter_bs)
        book_file = self._get_book_file_name(book_name)
        if self.debug:
            print("Use book file name ", book_file, "chapter number", len(chapter_bs))
        visited = []
        if self.downloadFile and os.path.exists(book_file):
            if self.debug:
                print("Delete file ", book_file)
            os.remove(book_file)
        for chapter in tqdm(chapter_bs):
            if self.debug:
                print("Start scratch chapter ", chapter, chapter.text, chapter.get('href'), chapter.string)
            chapter_name = chapter.string
            if not chapter_name:
                chapter_name = chapter.text
            url = chapter.get('href')
            if url in visited:
                continue
            visited.append(url)
            content_html = self.get_content_html(url)
            content_bs = self.get_chapter_bs(content_html, "content_root_element", "content_elements")
            if self.debug:
                print("Content length", len(content_bs))
            content = self._join_content(content_bs)
            if self.downloadFile:
                with open(book_file, 'a', encoding='utf-8') as f:
                    f.write(chapter_name)
                    f.write('\n')
                    f.write(content)
                    f.write('\n')

    def _get_website(self):
        url = self.get('url')
        splits = url.split('//')
        idx = splits[1].find('/')
        if idx < 0:
            return url
        return "{0}//{1}".format(splits[0], splits[1][0:idx])

    def get_content_html(self, url):
        if url.find('http') < 0:
            website = self._get_website()
            url = f"{website}{url}"
        req = requests.get(url=url)
        encoding = re.search('encoding=\"(.*)\"', req.text.split('\n')[0])[1]
        if not encoding:
            req.encoding = 'utf-8'
        else:
            req.encoding = encoding
        return req.text
