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

def workWords(soup) -> list[int]:
    chapters = soup.find_all('div', attrs={"class": "userstuff module"})
    word_count=[]
    for chapter in chapters:
        chapter = chapter.text
        chapter = chapter.lower()
        # getting rid of punctuations
        chapter.translate(punctuationTable)
        # because the find function takes in 2 extra unseen words
        word_count.append(len(chapter.split()) - 2)

    return word_count


def workWordFrequency(soup) -> dict:
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


def getWorkID(workLink: string):
    components = workLink.split("/")
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
        self.soup = str(soup)
        # titles and authors
        self.title = soup.find('h2').text.replace("\n", '').strip()

        self.author = soup.find(
            'h3', attrs={"class": "byline heading"}).text.replace("\n", '').split(',')

        # rating
        self.rating = soup.find(
            'dd', attrs={"class": "rating tags"}).text.replace("\n", "")

        # warnings
        self.warnings = []
        try: 
            for i in soup.find('dd', attrs={"class": "warning tags"}).find_all('li'):
                self.warnings.append(i.text)
        except AttributeError:
            pass

        # category
        self.categories = []
        try:
            for i in soup.find('dd', attrs={"class": "category tags"}).find_all('li'):
                self.categories.append(i.text)
        except AttributeError:
            pass

        # fandom
        self.fandom = []
        try:
            for i in soup.find('dd', attrs={"class": "fandom tags"}).find_all('li'):
                self.fandom.append(i.text)
        except:
            pass

        # relationships
        self.relationships = []
        try:
            for i in soup.find('dd', attrs={"class": "relationships tags"}).find_all('li'):
                self.relationships.append(i.text)
        except AttributeError:
            pass

        # characters
        self.characters = []
        try:
            for i in soup.find('dd', attrs={"class": "character tags"}).find_all('li'):
                self.characters.append(i.text)
        except AttributeError:
            pass

        # additional tags
        self.additional_tags = []
        try:
            for i in soup.find('dd', attrs={"class": "freeform tags"}).find_all('li'):
                self.additional_tags.append(i.text)
        except AttributeError:
            pass

        # language
        self.langauge=''
        try:
            self.language = soup.find(
                'dd', attrs={"class": "language"}).text.strip()
        except AttributeError:
            pass

        '''stats'''
        # publish date
        try:
            self.publish_date = soup.find('dd', attrs={"class": "published"}).text
        except AttributeError:
            self.publish_date = ''
        # last updated
        try:
            self.last_update = soup.find('dd', attrs={"class": "status"}).text
        except AttributeError:
            self.last_update = None

        # words
        try:
            words = soup.find('dd', attrs={"class": "words"})
            self.words = int(words.text.replace(',', ''))
        except AttributeError:
            self.words=0
        # chapter count
        try:
            chapters = soup.find('dd', attrs={"class": "chapters"})
            self.chapters = int(chapters.text.split('/')[0].replace(',', ''))
        except AttributeError:
            self.chapters=0
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
        try:
            self.hits = int(
                soup.find('dd', attrs={"class": "hits"}).text.replace(',', ''))
        except AttributeError:
            self.hits = 0
        '''links'''
        try:
            self.chapter_links = getChapterLinks(session, workID)
        except AttributeError:
            self.chapter_links = {}
        '''dunder methods'''

        def __str__(self):
            return "{} by {}".format(self.title, self.author)

        def toJSON() -> json:
            pass



if __name__ == "__main__" :
    session = requests.session()
    session.headers.update(HEADERS)
    session.cookies.update(COOKIES)


    worklink = "https://archiveofourown.org/works/58203763"
    workID = getWorkID(worklink)
    work = work(session, workID)

    workSoup=BS(work.soup,"html.parser")

    with open(f"{workID}.cache", 'w') as f:
        f.write(work.soup)

    count = workWords(workSoup)
    counts={}
    for i,c in enumerate(count):
        counts[i+1] = c

    plt.style.use('bmh')
    plt.figure(figsize=(12, 6))
    plt.rcParams["figure.dpi"] = 150
    plt.plot([x for x in range(1, len(counts)+1)], counts.values(),
             color="#12ACAE", marker='o', linestyle='-')
    plt.xlim(0.8, len(counts)+1)
    plt.ylim(1, sorted(list(counts.values()))[-1]+1000)
    plt.title(work.title)
    plt.xlabel('Chapter')
    plt.ylabel('Words')
    plt.xticks([x for x in range(0, len(counts)+5, 5)])
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(f"{workID}.png")
