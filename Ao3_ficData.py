import time
import string
import matplotlib.pyplot as plt
import matplotlib
import requests
from bs4 import BeautifulSoup as BS
# import asyncio
# import aiohttp
import os
import json

CACHE_FILE = "temp.json"
punctuation_1 = '!"#$%&()*+,–—./:;<=>?@[\\]^_`{|}~”“…\n'
punctuation_2 = "-'‘’\xa0\t"

'''the following could be used for preprocessing in the word count function via the translate meathod
letters = "abcdefghijklmnopqrstuvwxyz1234567890"
letterTTable = dict.fromkeys(map(ord, letters), None)
puncTTable = dict.fromkeys(map(ord, punctuation_1), " ")
for c in punctuation_2:
    puncTTable[ord(c)] = None'''

s = requests.session()
s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0',
                 'DNT': '1', 'Accept-Language': 'en-US,en:1=0.5', 'Referer': 'https://archiveofourown.org/works'})
s.cookies.update({'view_adult': 'true'})

# put the suffix of the fic here
site = "https://archiveofourown.org"
# Leidenschaft:/works/58203763/chapters/148205701
ficLink = "/works/58203763/chapters/148205701"
FIC = s.get(site+ficLink)
soup = BS(FIC.text, "html.parser")


class fic:
    def __init__(self, ficLink):
        soup = BS(get(ficLink).text, "html.parser")

        # titles and authors
        self.title = soup.find('h2').text.replace("\n", '').strip()

        self.author = soup.find(
            'h3', attrs={"class": "byline heading"}).text.replace("\n", '').split(',')

        '''metadata'''
        # rating
        self.rating = soup.find(
            'dd', attrs={"class": "rating tags"}).text.replace("\n", "")

        # warnings
        self.warnings = []
        for i in soup.find('dd', attrs={"class": "warning tags"}).findAll('li'):
            self.warnings.append(i.text)

        # category
        self.categories = []
        try:
            for i in soup.find('dd', attrs={"class": "category tags"}).findAll('li'):
                self.categories.append(i.text)
        except AttributeError:
            pass

        # fandom
        self.fandom = []
        for i in soup.find('dd', attrs={"class": "fandom tags"}).findAll('li'):
            self.fandom.append(i.text)

        # relationships
        self.relationships = []
        try:
            for i in soup.find('dd', attrs={"class": "relationships tags"}).findAll('li'):
                self.relationships.append(i.text)
        except AttributeError:
            pass

        # characters
        self.characters = []
        try:
            for i in soup.find('dd', attrs={"class": "character tags"}).findAll('li'):
                self.characters.append(i.text)
        except AttributeError:
            pass

        # additional tags
        self.additional_tags = []
        try:
            for i in soup.find('dd', attrs={"class": "freeform tags"}).findAll('li'):
                self.additional_tags.append(i.text)
        except AttributeError:
            pass

        # language
        self.language = soup.find('dd', attrs={"class": "language"}).text

        '''stats'''
        # publish date
        self.publish_date = soup.find('dd', attrs={"class": "published"}).text

        # last updated
        try:
            self.last_update = soup.find('dd', attrs={"class": "status"}).text

        except AttributeError:
            self.last_update = None

        # words
        words = soup.find('dd', attrs={"class": "words"})
        self.words = int(words.text.replace(',', ''))

        # chapter count
        chapters = soup.find('dd', attrs={"class": "chapters"})
        self.chapters = int(chapters.text.split('/')[0].replace(',', ''))

        # comments
        try:
            comments = soup.find('dd', attrs={"class": "comments"})
            self.comments = int(comments.text.replace(',', ''))
        except AttributeError:
            self.comments = None

        # kudos
        try:
            self.kudos = soup.find('dd', attrs={"class": "kudos"}).text
        except ValueError:
            self.kudos = int(
                soup.find('dd', attrs={"class": "kudos"}).text.replace(',', ''))
        except AttributeError:
            self.kudos = None

        # bookmarks
        try:
            self.bookmarks = int(
                soup.find('dd', attrs={"class": "bookmarks"}).text.replace(',', ''))
        except AttributeError:
            self.bookmarks = None

        # hits
        self.hits = int(
            soup.find('dd', attrs={"class": "hits"}).text.replace(',', ''))

        # TODO: Add all links and stuff on the page
        self.chapterLinks = getChapLinks(ficLink)


def get(ficLink):
    FIC = s.get(site+ficLink)

    while FIC.ok == False:

        if FIC.status_code in [404]:
            print("The link provided does not lead to a fanfic")
            return "a"
        elif FIC.status_code == 429:
            print("Rate limit reached waiting for a bit...")
            time.sleep(100)
            FIC = s.get(site+ficLink)
        else:
            i = 2
            print(f"Error {FIC.status_code} occured. Retrying...")
            FIC = s.get(site+ficLink)
    return FIC

# traversing through the chapters


def findNext(ficLink):
    for i in soup.findAll('a'):
        if "Next Chapter →" in i:
            return i.get('href')


def chapterWords(soup):
    chapter = soup.find('div', attrs={"class": "userstuff module"})
    output = chapter.text
    output = output.lower()
    # getting rid of punctuations
    for c in punctuation_1:
        output = output.replace(c, " ")
    for c in punctuation_2:
        output = output.replace(c, "")
    # because the find function takes in 2 extra unseen words
    return (len(output.split())-2)


def WordFreq(ficLink):
    Fic = s.get(site+ficLink)
    soup = BS(Fic.text, "html.parser")
    freq = {}
    print("1")
    while findNext(soup) != None:
        print("2")
        Fic = s.get(site+ficLink)
        soup = BS(Fic.text, "html.parser")
        chapter = soup.find('div', attrs={"class": "userstuff module"})
        output = chapter.text
        output = output.lower()
        output = output.translate(puncTTable)
        for i in output.split():
            if i in freq:
                freq[i] += 1
            else:
                freq[i] = 1
        ficLink = findNext(soup)
    del freq["chapter"]
    del freq["text"]
    return freq


def PunctuationFrequency():
    chapter = soup.find('div', attrs={"class": "userstuff module"})
    output = chapter.text
    output = output.lower()
    output = output.translate(letterTTable)
    for c in punctuation:
        output = output.replace(c, f"{c} ")
    return output.split()


def getChapLinks(ficLink):
    links = {}
    ficLinkComps = ficLink.split("/")
    indexLink = "/" + ficLinkComps[1] + "/" + ficLinkComps[2] + "/navigate"
    index = s.get(site+indexLink)
    soup = BS(index.text, "html.parser")

    linkList = list(map(lambda x: x.get('href'), soup.find('ol').findAll('a')))
    for i in range(1, len(linkList)+1):
        links[f'{i}'] = linkList[i-1]
    return links


def getWordCounts(ficLink, fic) -> dict:
    cache = {}
    if os.path.exists(CACHE_FILE) and os.path.getsize(CACHE_FILE) > 0:
        try:
            with open(CACHE_FILE, "r") as f:
                cache = json.load(f)
        except json.decoder.JSONDecodeError:
            print(
                f"Warning: Invalid JSON in {CACHE_FILE}. Starting with empty cache.")

    fic_title = fic.title
    if fic_title not in cache:
        cache[fic_title] = {}

    for i in range(1, fic.chapters+1):
        chapter_key = str(i)
        if chapter_key in cache[fic_title]:
            continue
        else:
            res = get(fic.chapterLinks[chapter_key])
            soup = BS(res.text, "html.parser")
            cache[fic_title][chapter_key] = chapterWords(
                soup)

    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=4)

    return cache[fic_title]


if __name__ == "__main__":
    print("main start")
    Fic = fic(ficLink)
    title = Fic.title
    chapters = Fic.chapters

    st = time.time()
    counts = getWordCounts(ficLink, Fic)
    print(time.time()-st)

    plt.style.use('bmh')
    plt.figure(figsize=(12, 6))
    plt.rcParams["figure.dpi"] = 150
    plt.plot([x for x in range(1, len(counts)+1)], counts.values(),
             color="#12ACAE", marker='o', linestyle='-')
    plt.xlim(0.84, len(counts)+1)
    plt.ylim(1, sorted(list(counts.values()))[-1]+1000)
    plt.title(title)

    plt.xlabel('Chapter')
    plt.ylabel('Words')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(f"{title}_{len(counts)}.png")

plt.show()
