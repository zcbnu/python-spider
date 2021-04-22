import requests
from bs4 import BeautifulSoup
import spiderUtils
from BookPathGuess import BookPathGuess
import json


def guess_book_url(book_name, json):
    if "guess_book" in json:
        type_class = json["guess_book"]["type"]
        guess_book = globals()[type_class](json)
        if isinstance(guess_book, IGuessBook):
            return guess_book.guess_url(book_name)


class IGuessBook:
    def guess_url(self, book_name): pass


class BookSearch(IGuessBook):

    def guess_url(self, book_name):
        if self.config is None:
            raise Exception("Guess url failed since not 'guess_book' field. json:{0}".format(self.json))
        url = self.config["search_url"].format(book_name)
        print("URL", url)
        response = requests.get(url=url)
        site = self.json['url']
        if 'encoding' in self.json:
            response.encoding = self.json['encoding']
        else:
            response.encoding = 'utf-8'
        response_bs = BeautifulSoup(response.text, 'lxml')
        elements = spiderUtils.get_page_elements(response_bs, self.config['check_element'])
        for element in elements:
            title = element.get('title')
            if title.find(book_name) < 0:
                continue
            result_url = "{0}/{1}".format(site, element.get('href'))
            print(result_url)
            response = requests.get(result_url)
            if 'encoding' in self.json:
                response.encoding = self.json['encoding']
            else:
                response.encoding = 'utf-8'
            return response.text, result_url

    def __init__(self, json):
        self.json = json
        self.config = None
        if "guess_book" in json:
            self.config = json["guess_book"]


class GuessByName(IGuessBook):

    def guess_url(self, book_name):
        if self.config is None:
            raise Exception("Guess url failed since not 'guess_book' field. json:{0}".format(self.json))

        url = self.json["url"]
        prefix_list = []
        if "second_dir_elements" in self.config:
            elements = self._second_dir_elements(url)
            for e in elements:
                prefix_list.append("{0}/{1}".format(url, e.get('href')))
        else:
            prefix_list.append(url)
        for guess in BookPathGuess(book_name):
            for prefix in prefix_list:
                target = "{0}/{1}/".format(prefix, guess)
                try:
                    result = self.get_content_html(target)
                except:
                    result = self.config["failure_str"]
                print("prefix==", target)
                if self._check_book_index_page_valid(result):
                    return result, target
        return False, False

    def get_content_html(self, url):
        if url.find('http') < 0:
            website = self._get_website()
            url = f"{website}{url}"
        resp = requests.get(url=url)
        if 'encoding' in self.json:
            resp.encoding = self.json['encoding']
        else:
            resp.encoding = 'utf-8'
        return resp.text

    def _second_dir_elements(self, html):
        response_bs = BeautifulSoup(self.get_content_html(html), 'lxml')
        elements = self.config["second_dir_elements"]
        results = spiderUtils.get_page_elements(response_bs, elements)
        return results

    def _check_book_index_page_valid(self, html):
        return html.find(self.config["failure_str"]) < 0

    def _get_website(self):
        url = self.json['url']
        splits = url.split('//')
        idx = splits[1].find('/')
        if idx < 0:
            return url
        return "{0}//{1}".format(splits[0], splits[1][0:idx])

    def __init__(self, json):
        self.json = json
        self.config = None
        if "guess_book" in json:
            self.config = json["guess_book"]

