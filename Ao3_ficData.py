import os
import json
import time
import string
from textParsing import *
from dataRetrieve import *
import requests
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup as BS


'''TODO[
    Async requests to get stuff faster
    Save the data using the fic ids instead of their name to allow multiple fics with same name to be saved simultaneously
]'''

CACHE_FILE = "./cache/cache.json"
HEADERS = {'User-Agent': 'Web scraper for scraping meta data from fics (https://github.com/FenrisI/AO3-FicsData)',
           'DNT': '1',
           'Accept-Language': 'en-US,en:1=0.5',
           'Referer': 'https://archiveofourown.org/works'}
COOKIES = {'view_adult': 'true'}

SITE = "https://archiveofourown.org"


class fic:
    def __init__(self,  session, ficLink):
        soup = BS(get(session, ficLink).text, "html.parser")

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
        self.chapterLinks = getChapterLinks(session, ficLink)

        '''dunder methods'''

        def __str__(self):
            "{} by {}".format(self.title, self.author)


def getWordCounts(fic) -> dict:
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


def getFicID(ficLink: string):
    components = ficLink.split("/")
    return components[4]


if __name__ == "__main__":

    session = requests.session()
    session.headers.update(HEADERS)
    session.cookies.update(COOKIES)

    # NOTE Change the link here to the one for the fic you want the graph for
    ficLink = "https://archiveofourown.org/works/58203763/chapters/148881631"

    Fic = fic(session, ficLink)
    title = Fic.title
    chapters = Fic.chapters
    chapterLinks = Fic.chapterLinks

    counts = getWordCounts(Fic)
    print(counts)
    session.close()

    plt.style.use('bmh')
    plt.figure(figsize=(12, 6))
    plt.rcParams["figure.dpi"] = 150
    plt.plot([x for x in range(1, len(counts)+1)], counts.values(),
             color="#12ACAE", marker='o', linestyle='-', )
    plt.xlim(0.8, len(counts)+1)
    plt.ylim(1, sorted(list(counts.values()))[-1]+1000)
    plt.title(title)
    plt.xlabel('Chapter')
    plt.ylabel('Words')
    plt.xticks([x for x in range(0, len(counts)+5, 5)])
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(f"graphs/{title}_{len(counts)}.png")

    plt.show()
