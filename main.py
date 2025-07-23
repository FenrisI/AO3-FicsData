import os
import json
import time
import requests
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup as BS
import string

PUNCTUATION_1 = '!"#$%&()*+,–—./:;<=>?@[\\]^_`{|}~”“…\n'
PUNCTUATION_2 = "-'‘’\xa0\t"
LETTERS = "abcdefghijklmnopqrstuvwxyz1234567890"
SITE = "https://archiveofourown.org/"
CACHE_FILE = "./cache/cache.json"
HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0',
           'DNT': '1',
           'Accept-Language': 'en-US,en:1=0.5',
           'Referer': 'https://archiveofourown.org/works'}
COOKIES = {'view_adult': 'true'}

SITE = "https://archiveofourown.org"


# creating translation tables for text parsing
letterTable = dict.fromkeys(map(ord, LETTERS), None)
punctuationTable = dict.fromkeys(map(ord, PUNCTUATION_1), " ")

for c in PUNCTUATION_2:
    punctuationTable[ord(c)] = None


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


def getFicID(ficLink: string):
    components = ficLink.split("/")
    return components[4]


def get(session: requests.Session, Link: str, retry: int = 3) -> requests.models.Response:
    res = session.get(Link)
    if res.ok:
        return res
    elif res.status_code == 404:
        print("Error 404:\n\tPage not found")
        return None
    elif res.status_code == 429:
        print("Error 429:\n\tRate limit reached waiting for a bit...")
        time.sleep(30)
        res = get(session, Link)
    else:
        while retry > 0:
            get(session, Link, retry=retry-1)
    return None


def getWork(session: requests.Session, workID: str) -> BS:
    completeWorkLink = SITE + "/works/" + workID + "?view_full_work=true"
    print("\n"+workID)
    print(completeWorkLink)
    res = get(session, completeWorkLink)
    try: 
        workSoup = BS(res.text, "html.parser")
    except AttributeError:
        return None
    return workSoup


def getChapterLinks(session: requests.Session, workID: str) -> dict:
    navPageLink = SITE + "/works/" + workID + "/navigate"
    links = {}
    navPage = get(session, navPageLink)
    soup = BS(navPage.text, "html.parser")
    linkList = list(map(lambda x: x.get('href'),
                    soup.find('ol').find_all('a')))
    for i in range(1, len(linkList)+1):
        links[f'{i}'] = linkList[i-1]
    return links

class work:
    def __init__(self,  session, workID):
        soup = getWork(session, workID)
        
        if soup == None:
            return None
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
        self.language = soup.find(
            'dd', attrs={"class": "language"}).text.strip()

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
        self.chapter_links = getChapterLinks(session, workID)

        '''dunder methods'''

        def __str__(self):
            return "{} by {}".format(self.title, self.author)

        def toJSON() -> json:
            pass



if __name__ == "__main__" :
    session = requests.session()
    session.headers.update(HEADERS)
    session.cookies.update(COOKIES)


    ficlink = input("Enter the link for the fic:")
    ficID = getFicID(ficlink)
    print(ficID)
    fic = work(session, ficID)
    print(fic.chapter_links)
