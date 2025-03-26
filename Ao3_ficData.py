import string
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup as BS
import os
import json

CACHE_FILE = "cache.json"
HEADERS = {'User-Agent': 'Web scraper for scraping meta data from fics (https://github.com/FenrisI/AO3-FicsData)',
           'DNT': '1',
           'Accept-Language': 'en-US,en:1=0.5',
           'Referer': 'https://archiveofourown.org/works'}
COOKIES = {'view_adult': 'true'}
PUNCTUATION_1 = '!"#$%&()*+,–—./:;<=>?@[\\]^_`{|}~”“…\n'
PUNCTUATION_2 = "-'‘’\xa0\t"
LETTERS = "abcdefghijklmnopqrstuvwxyz1234567890"
SITE = "https://archiveofourown.org"

# creating translation tables for text parsing
letterTable = dict.fromkeys(map(ord, letters), None)
punctuationTable = dict.fromkeys(map(ord, PUNCTUATION_1), " ")
for c in PUNCTUATION_2:
    punctuationTable[ord(c)] = None


class fic:
    def __init__(self, ficLink):
        soup = BS(get(ficLink).text, "html.parser")

        '''metadata'''
        # titles and authors
        self.title = soup.find('h2').text.replace("\n", '').strip()

        self.author = soup.find(
            'h3', attrs={"class": "byline heading"}).text.replace("\n", '').split(',')

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
            self.comments = 0

        # kudos
        try:
            self.kudos = soup.find('dd', attrs={"class": "kudos"}).text
        except ValueError:
            self.kudos = int(
                soup.find('dd', attrs={"class": "kudos"}).text.replace(',', ''))
        except AttributeError:
            self.kudos = 0

        # bookmarks
        try:
            self.bookmarks = int(
                soup.find('dd', attrs={"class": "bookmarks"}).text.replace(',', ''))
        except AttributeError:
            self.bookmarks = 0

        # hits
        self.hits = int(
            soup.find('dd', attrs={"class": "hits"}).text.replace(',', ''))

        '''links'''
        self.chapterLinks = getChapterLinks(ficLink)

        '''dunder methods'''

        def __str__(self):
            "{} by {}".format(self.title, self.author)


def get(ficLink) -> requests.models.Response:
    if ficLink.split("/")[1] == "works":
        FIC = s.get(site+ficLink)
    else:
        FIC = s.get(ficLink)

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


def chapterWords(soup) -> int:
    chapter = soup.find('div', attrs={"class": "userstuff module"})
    chapter = chapter.text
    chapter = chapter.lower()
    # getting rid of punctuations
    chapter.translate(punctuationTable)
    # because the find function takes in 2 extra unseen words
    wordCount = len(chapter.split()) - 2

    return wordCount


def chapterWordFrequency(soup) -> dict:
    frequency = {}
    chapter = soup.find('div', attrs={"class": "userstuff module"})
    chapter = chapter.text
    chapter = chapter.lower()
    chapter = chapter.translate(punctuationTable)
    for i in chapter.split():
        if i in frequency:
            frequency[i] += 1
        else:
            frequency[i] = 1
    frequency["chapter"] -= 1
    frequency["text"] -= 1
    return frequency


def chapterPunctuationFrequency(soup) -> dict:
    frequency = {}
    chapter = soup.find('div', attrs={"class": "userstuff module"})
    chapter = chapter.text.lower()
    chapter = chapter.translate(letterTable)
    for i in chapter:
        if i in frequency:
            frequency[i] += 1
        else:
            frequency[i] = 1

    return frequency


def getChapterLinks(ficLink) -> dict:
    links = {}
    ficLinkComps = ficLink.split("/")
    if ficLinkComps[1] == "works":
        indexLink = "/" + ficLinkComps[1] + "/" + ficLinkComps[2] + "/navigate"
    else:
        indexLink = "/" + ficLinkComps[3] + "/" + ficLinkComps[4] + "/navigate"
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
            print(f"Chapter {i} is in cache")
            continue
        else:
            res = get(fic.chapterLinks[chapter_key])
            soup = BS(res.text, "html.parser")
            print(f"Chapter {i} is not in cache. Fetching word count...")
            cache[fic_title][chapter_key] = chapterWords(soup)

    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=4)

    return cache[fic_title]


if __name__ == "__main__":
    s = requests.session()
    s.headers.update(HEADERS)
    s.cookies.update(COOKIES)

    # NOTE Change the link here to the one for the fic you want the graph for
    ficLink = "https://archiveofourown.org/works/58203763/chapters/148881631"

    Fic = fic(ficLink)
    title = Fic.title
    chapters = Fic.chapters

    counts = getWordCounts(ficLink, Fic)

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
