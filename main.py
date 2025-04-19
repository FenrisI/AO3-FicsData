# from Ao3_ficData import *
from textParsing import *
# from dataRetrieve import *
from work import *
from constants import *


ses = requests.Session()
ses.headers.update(HEADERS)
ses.cookies.update(COOKIES)
chapters = {}
workID = "58203763"
print("AAAAAAAAAAA")

x = time.time()
fic = work(ses, workID)
with open(CACHE_FILE, '+w') as cache:
    cache.write(fic)

print(time.time()-x)
