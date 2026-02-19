import requests
from bs4 import BeautifulSoup as BS
from scrapper import *
from analytics import *

class ResponseError(Exception):
    pass

class Work:

    def __init__(self,  session, work_id):
        self.session = session
        self.work_id = work_id
        self.soup = None
        self.title = None
        self.author = None
        self.rating = None
        self.warning = None
        self.categories = None
        self.fandom = None
        self.relationships = None
        self.characters = None
        self.additional_tags = None
        self.langauge = None
        self.publish_date = None
        self.last_update = None
        self.word_count = None
        self.chapters = None
        self.comments = None
        self.kudos = None
        self.bookmarks=None
        self.hits = None
        self.chapter_links = None
        self.chapter_word_counts = None
        self.chapter_punctuation_frequencies = None
        self.punctuation_frequency = None
        self.chapter_word_frequencies = None
        self.work_word_frequency = None
        
    def fetch_data(self):
        soup = get_work(self.session, self.work_id)
        
        if soup == None:
            raise ResponseError(f"Could not retrieve work with ID: {self.work_id}")
        else:
            self.soup = str(soup)
        
        '''metadata'''
        # title
        self.title = soup.find('h2').text.replace("\n", '').strip()
        
        #author
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
        try:
            self.language = soup.find(
                'dd', attrs={"class": "language"}).text.strip()
        except AttributeError:
            self.langauge=''

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

        # word_count
        try:
            word_count = soup.find('dd', attrs={"class": "word_count"})
            self.word_count = int(word_count.text.replace(',', ''))
        except AttributeError:
            self.word_count=0

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
            self.chapter_links = get_chapter_links(self.session, self.work_id)
        except AttributeError:
            self.chapter_links = {}
    
    def calculate_stats(self):
        soup: BeautifulSoup = BS(self.soup, "html.parser")
        self.chapter_word_counts: dict[int, int] = chapter_word_counts(soup)
        self.chapter_punctuation_frequencies: FrequencyMap = chapter_punctuation_frequency(soup)
        self.punctuation_frequency: FrequencyMap = work_punctuation_frequency(self.chapter_punctuation_frequencies)
        self.chapter_word_frequencies: FrequencyMap = chapter_word_frequency(soup)
        self.work_word_frequency: FrequencyMap = work_word_frequency(self.chapter_word_frequencies)

    '''dunder methods'''
    def __str__(self):
        return "{} by {}".format(self.title, self.author)


if __name__ == "__main__":
    session = requests.Session()
    COOKIES = {'view_adult': 'true'}
    session.cookies.update(COOKIES)
    w = Work(session, 54890437)
    w.fetch_data()
    w.calculate_stats()