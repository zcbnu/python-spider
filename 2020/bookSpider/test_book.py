import os
import sys
import traceback
from bookSite import BookSite
from BookPathGuess import BookPathGuess

if __name__ == '__main__':
    site = BookSite(file="siteConfig/99csw.json", debug=False, download=True)
    site.scratch_book("毛泽东选集")

    # book_name = "人类简史"
    # if len(sys.argv) > 1:
    #     book_name = sys.argv[1]
    #
    # dirPath = "siteConfig/"
    # for f in os.listdir(dirPath):
    #     siteConfig = os.path.join(dirPath, f)
    #     site = BookSite(file=siteConfig, download=True, debug=False)
    #     try:
    #         site.scratch_book(book_name)
    #     except:
    #         traceback.print_exc()
    #     finally:
    #         if os.path.exists('{0}.txt'.format(book_name)):
    #             break

