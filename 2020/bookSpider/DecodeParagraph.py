import re
import base64
from bs4 import BeautifulSoup

def decode_paragraph(paragraphs, base_bs, json):
    if "decode_paragraph" in json:
        cls = json["decode_paragraph"]
        decoder = globals()[cls]()
        if isinstance(decoder, IDecodeParagraph):
            return decoder.decode(paragraphs, base_bs)
        else:
            raise Exception("Unknown DecodeParagraph class set in param: 'decode_paragraph' class name {0}".format(cls))
    return paragraphs


class IDecodeParagraph:
    def decode(self, paragraphs, base_bs): pass


class DefaultDecodeParagraph(IDecodeParagraph):
    def decode(self, paragraphs, base_bs):
        return paragraphs


class CswDecodeParagraph(IDecodeParagraph):
    def decode(self, paragraphs, base_bs):
        meta_bs = base_bs.find_all('meta')
        s = meta_bs[4].get('content')
        order = _gen_list_for_csw(s)
        ret = []
        if len(order) != len(paragraphs):
            print("order:", len(order), "content", len(paragraphs))
        for idx in order:
            ret.append(paragraphs[idx])
        return ret


def _gen_list_for_csw(s, encoding='utf-8'):
    ss = base64.decodebytes(bytes(s, encoding)).decode(encoding)
    sl = re.split(u'[A-Z]+%', ss)
    ret = [0] * len(sl)
    i = 0
    j = 0
    for s in sl:
        e = int(s)
        if e < 3:
            ret[e] = i
            j += 1
        else:

            ret[e - j] = i
            j += 2
        i += 1
    return ret


if __name__ == "__main__":
    ts = "NTRWJTM0TSU1MFIlMjBWJTUzSiU0NkglMjFSJTM5VCU1NFolODBFJTM3RyU3M0slNjhBJTkwViU1OFUlODVTJTQwTiU4Mk8lNzNXJTY0TiU3M0wlNjNXJTk0TiU1M0olNzZXJTEwNkwlOTlZJTExNUclODdWJTgyTCU3ME4lMTIyRSU5M1klMlklMTA3TSU5Nk4lMTM0SSUxVCU4NkQlMTM1TCU5NFIlOThLJTkzWiU4N0klMTA1TiUxMDhDJTExMlglMTI3QyUxNDNHJTE0OUclMTIxQyUxNTJUJTE0NFQlMTA4RiUxNDdaJTE0MlIlMTE1TCUxNTVFJTEyN1ElMFolMTc0TyUxMzREJTE2MEclMTI5WiUxODM="
    with open('test.txt', 'r', encoding='utf-8') as f:
        html = f.read()
        gl = _gen_list_for_csw(ts)
        print(gl, len(gl), max(gl))
        bs = BeautifulSoup(html, 'lxml')
        content_bs = bs.find("dd", id='content')
        contents_bs = content_bs.find_all('div')
        # contents_bs = filter(lambda i: i.get("class") is not None, contents_bs)
        tmp_bs = []
        for t_bs in contents_bs:
            if t_bs.get("class") is None:
                tmp_bs.append(t_bs)
        contents = [i.text for i in tmp_bs]
        csw = CswDecodeParagraph()
        ret = csw.decode(contents, bs)
        print(len(contents))
        for i in range(len(contents)):
            # print("[{0}]".format(i), contents[i])
            print(ret[i])
