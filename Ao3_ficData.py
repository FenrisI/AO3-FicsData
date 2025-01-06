from bs4 import BeautifulSoup as BS
import requests
import matplotlib
import matplotlib.pyplot as plt
from pandas import DataFrame
import string


punctuation_1='!"#$%&()*+,–—./:;<=>?@[\\]^_`{|}~”“…\n'
punctuation_2="-'‘’\xa0\t"

letters="abcdefghijklmnopqrstuvwxyz1234567890"
letterTTable = dict.fromkeys(map(ord, letters), None)
puncTTable = dict.fromkeys(map(ord, punctuation_1), " ")
for c in punctuation_2:
    puncTTable[ord(c)]=None

#put the suffix of the fic here
ficLink = "/works/45479821/chapters/114431764"
Fic = requests.get(site+ficLink)
soup = BS(Fic.text, "html.parser")

class fic:
    def __init__(self,ficLink):
        soup = BS(requests.get("https://archiveofourown.org"+ficLink).text, "html.parser")

        #titles and authors
        self.title = soup.find('h2').text.replace("\n",'').strip()
        self.author= soup.find('h3',attrs={"class":"byline heading"}).text.replace("\n",'').split(',')

        '''metadata'''
        #rating
        self.rating = soup.find('dd',attrs={"class":"rating tags"}).text.replace("\n","")

        #warnings
        self.warnings=[]
        for i in soup.find('dd',attrs={"class":"warning tags"}).findAll('li'):
            self.warnings.append(i.text)
            
        #category
        self.categories=[]
        try:
            for i in soup.find('dd',attrs={"class":"category tags"}).findAll('li'):
                self.categories.append(i.text)
        except AttributeError:
            pass

        #fandom
        self.fandom=[]
        for i in soup.find('dd',attrs={"class":"fandom tags"}).findAll('li'):
            self.fandom.append(i.text)  

        #relationships
        self.relationships=[]
        try:
            for i in soup.find('dd',attrs={"class":"relationships tags"}).findAll('li'):
                self.relationships.append(i.text)
        except AttributeError:
            pass

        #characters
        self.characters=[]
        try:
            for i in soup.find('dd',attrs={"class":"character tags"}).findAll('li'):
                self.characters.append(i.text)
        except AttributeError:
            pass

        #additional tags
        self.additional_tags=[]
        try:
            for i in soup.find('dd',attrs={"class":"freeform tags"}).findAll('li'):
                self.additional_tags.append(i.text)
        except AttributeError:
            pass

        #language
        self.language=soup.find('dd',attrs={"class":"language"}).text

        '''stats'''
        #publish date
        self.publish_date = soup.find('dd',attrs={"class":"published"}).text
        

        #last updated
        try:
            self.last_update = soup.find('dd',attrs={"class":"status"}).text
            
        except AttributeError:
            self.last_update=None
    
        #words
        words = soup.find('dd',attrs={"class":"words"})
        self.words = int(words.text.replace(',',''))
           
        #chapter count
        chapters = soup.find('dd',attrs={"class":"chapters"})
        self.chapters = int(chapters.text.split('/')[0].replace(',',''))
        
        #comments
        try:
            comments = soup.find('dd',attrs={"class":"comments"})
            self.comments = int(comments.text.replace(',',''))
        except AttributeError:
            self.comments=None
    
        #kudos
        try:
            self.kudos = soup.find('dd',attrs={"class":"kudos"}).text
        except ValueError:
            self.kudos = int(soup.find('dd',attrs={"class":"kudos"}).text.replace(',',''))
        except AttributeError:
            self.kudos=None       
    
        #bookmarks
        try:    
            self.bookmarks = int(soup.find('dd',attrs={"class":"bookmarks"}).text.replace(',',''))
        except AttributeError:
            self.bookmarks=None
            
        #hits
        self.hits = int(soup.find('dd',attrs={"class":"hits"}).text.replace(',',''))
        

#traversing through the chapters
def findNext(ficLink):
    for i in soup.findAll('a'):
        if "Next Chapter →" in i:
            return i.get('href')



def chapterWords():
    chapter = soup.find('div',attrs={"class":"userstuff module"})
    output = chapter.text 
    output = output.lower()
    #getting rid of punctuations
    for c in punctuation_1:
            output = output.replace(c," ")
        for c in punctuation_2:
            output = output.replace(c,"")
    return (len(output.split())-2) #because the find function takes 2 extra words

def WordFreq(ficLink):
    Fic = requests.get(site+ficLink)
    soup = BS(Fic.text, "html.parser")
    freq={}
    print("1")
    while findNext(soup) != None:
        print("2")
        Fic = requests.get(site+ficLink)
        soup = BS(Fic.text, "html.parser")
        chapter = soup.find('div',attrs={"class":"userstuff module"})
        output = chapter.text
        output = output.lower()
        output = output.translate(puncTTable)
        for i in output.split():
            if i in freq:
                freq[i]+=1
            else:
                freq[i]=1
        ficLink = findNext(soup)
    del freq["chapter"]
    del freq["text"]
    return freq
    

def PunctuationFrequency():
    chapter = soup.find('div',attrs={"class":"userstuff module"})
    output = chapter.text
    output = output.lower()
    output = output.translate(letterTTable)
    for c in punctuation:
        output = output.replace(c,f"{c} ")
    return output.split()

def graphBar(dic,title,xLab,counts):    
    plt.bar(x=dic.keys(),height=dic.values(),color="#12ACAE")
    plt.title(title)
    plt.xlabel(xLab)
    plt.ylabel("Frequency")
    plt.savefig(f"{title.split()[:4]}_{len(counts)}.png")
    plt.show()


if __name__ == "__main__":
    counts=[]
    puncs={}


    title= soup.find('h2').text.replace("\n",'').strip()

    while findNext(ficLink) != None:
        Fic = requests.get(site+ficLink)
        soup = BS(Fic.text, "html.parser")
        counts.append(chapterWords())
        ficLink = findNext(ficLink)

    plt.style.use('classic')
    plt.rcParams["figure.dpi"] = 150
    plt.tight_layout(pad=2.5)
    plt.plot([i for i in range(1,len(counts)+1)],counts, color="#12ACAE")
    plt.xlim(1, len(counts)+1)
    plt.ylim(0, max(counts)+2000)
    plt.title(title)
    
    plt.xlabel('Chapter')
    plt.ylabel('Words')
    plt.grid()
    plt.savefig(f"{title}_{len(counts)}.png")

    plt.show()
