import time
import requests
from bs4 import BeautifulSoup as BS

SITE = "https://archiveofourown.org/"


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
    completeWorkLink = SITE + "works/" + workID + "?view_full_work=true"
    res = get(session, completeWorkLink)
    workSoup = BS(res.text, "html.parser")
    return workSoup


def getChapterLinks(session: requests.Session, workID: str) -> dict:
    navPageLink = SITE + "works/" + workID + "/navigate"
    links = {}
    navPage = get(session, navPageLink)
    soup = BS(navPage.text, "html.parser")
    linkList = list(map(lambda x: x.get('href'),
                    soup.find('ol').find_all('a')))
    for i in range(1, len(linkList)+1):
        links[f'{i}'] = linkList[i-1]
    return links


if __name__ == "__main__":
    import requests
    session = requests.Session()
    work = getWork(session, 58203763)
    print(work.text[:50])
    session.close()
