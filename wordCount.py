from bs4 import BeautifulSoup as BS
import requests
import matplotlib
import matplotlib.pyplot as plt
from pandas import DataFrame
import string
import time

punctuation_1='!"#$%&()*+,–—./:;<=>?@[\\]^_`{|}~”“…\n'
punctuation_2="-'‘’\xa0\t"
letters="abcdefghijklmnopqrstuvwxyz1234567890"
s = requests.session()
s.headers.update({'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0', 'DNT':'1', 'Accept-Language':'en-US,en:1=0.5', 'Referer':'https://archiveofourown.org/works'})
s.cookies.update({'view_adult':'true'})

site="https://archiveofourown.org"
ficLink = "/works/58203763/chapters/148205701"

letterTTable = dict.fromkeys(map(ord, letters), None)
puncTTable = dict.fromkeys(map(ord, punctuation_1), " ")
for c in punctuation_2:
    puncTTable[ord(c)]=None

def findNext(ficLink):
    for i in soup.findAll('a'):
        if "Next Chapter →" in i:
            return i.get('href')

def chapterWords():
    chapter = soup.find('div',attrs={"class":"userstuff module"})
    output = chapter.text 
    output = output.lower()
    #getting rid of punctuations
    output.translate(puncTTable)

    return (len(output.split())-2)


soup = BS(s.get(site+ficLink).text, "html.parser")
counts = []

start=time.time()
while findNext(ficLink) != None:
        
        print("....")
        t=time.time()
        FIC=s.get(site+ficLink)
        print(FIC.ok)
        while FIC.status_code!=200:
            FIC=s.get(site+ficLink)
        print(time.time()-t)
        soup = BS(FIC.text, "html.parser")

        
        counts.append(chapterWords())
        ficLink = findNext(ficLink)
diff = time.time() - start

print(diff)
plt.style.use('classic')
plt.rcParams["figure.dpi"] = 150
plt.tight_layout(pad=2.5)
plt.plot([i for i in range(1,len(counts)+1)],counts, color="#12ACAE")
plt.xlim(1, len(counts)+1)
plt.ylim(0, sorted(counts)[-1])
plt.title("title here")

plt.xlabel('Chapter')
plt.ylabel('Words')
plt.grid()
#plt.savefig(f"{title}_{len(counts)}.png")
plt.show()
