from dataRetrieve import *


class work:
    def __init__(self,  session, workID):
        soup = getWork(session, workID)

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
            "{} by {}".format(self.title, self.author)
