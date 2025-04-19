HEADERS = {'User-Agent': 'Web scraper for scraping meta data from fics (https://github.com/FenrisI/AO3-FicsData)',
           'DNT': '1',
           'Accept-Language': 'en-US,en:1=0.5',
           'Referer': 'https://archiveofourown.org/works'}
COOKIES = {'view_adult': 'true'}

SITE = "https://archiveofourown.org/"
CACHE_FILE = "./cache/cache1.json"

PUNCTUATION_1 = '!"#$%&()*+,–—./:;<=>?@[\\]^_`{|}~”“…\n'
PUNCTUATION_2 = "-'‘’\xa0\t"
LETTERS = "abcdefghijklmnopqrstuvwxyz1234567890"
# creating translation t`ables for text parsing
letterTable = dict.fromkeys(map(ord, LETTERS), None)
punctuationTable = dict.fromkeys(map(ord, PUNCTUATION_1), " ")
for c in PUNCTUATION_2:
    punctuationTable[ord(c)] = None
