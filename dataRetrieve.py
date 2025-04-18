import requests
from bs4 import BeautifulSoup as BS
import time
from textParsing import *

SITE = "https://archiveofourown.org/work/"


def get(session, ficID, retry=3) -> requests.models.Response:
    res = session.get(SITE+ficID)
    retries = retry

    if res.ok:
        return res
    if res.status_code == 404:
        print("The link provided does not lead to a fnfic")
        return None
    elif res.status_code == 429:
        print("Rate limit reached waiting for a bit...")
        time.sleep(30)
        res = get(session, SITE+ficID)
    while retry > 0:
        get(session, SITE+ficID, retry=retries-1)


def getChapterLinks(session, ficID) -> dict:
    links = {}
    indexLink = SITE+ficID+"/navigate"
    index = get(session, SITE+indexLink)
    soup = BS(index.text, "html.parser")
    linkList = list(map(lambda x: x.get('href'), soup.find('ol').findAll('a')))
    for i in range(1, len(linkList)+1):
        links[f'{i}'] = linkList[i-1]
    return links
