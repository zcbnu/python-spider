import re
from zhon.hanzi import punctuation
from pypinyin import pinyin, lazy_pinyin


class BookPathGuess:

    def __init__(self, book_name):
        self.book_name = book_name
        self.guessCount = 0
        s_book_name = re.sub(u"[%s]+" % punctuation, "", book_name)
        self.s_book_name = s_book_name
        length = len(s_book_name)
        self.names = []
        self.cur = 0
        if length == 1:
            self.names.append(lazy_pinyin(s_book_name))
            return
        for x in range(length):
            if x > 0:
                name = self.s_book_name[x:]
                if len(name) > 1:
                    self.names.append(lazy_pinyin(name))
            name = self.s_book_name[0:x+1]
            if len(name) > 1:
                self.names.append(lazy_pinyin(name))

    def __iter__(self):
        self.cur = 0
        return self

    def __next__(self):
        if self.cur == len(self.names):
            raise StopIteration
        else:
            result = self.names[len(self.names) - self.cur - 1]
            self.cur += 1
            return ''.join(result)

