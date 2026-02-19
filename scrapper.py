import requests
import time
from bs4 import BeautifulSoup as BS

SITE = "https://archiveofourown.org/"

def get_work_id(workLink: str):
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

def get_work(session: requests.Session, work_id: str) -> BS:
    completeWorkLink = SITE + "/works/" + work_id + "?view_full_work=true"
    res = get(session, completeWorkLink)
    try: 
        workSoup = BS(res.text, "html.parser")
    except AttributeError:
        return None
    return workSoup

def get_chapter_links(session: requests.Session, work_id: str) -> dict:
    nav_page_link = SITE + "/works/" + work_id + "/navigate"
    links = {}
    nav_page = get(session, nav_page_link)
    soup = BS(nav_page.text, "html.parser")
    linkList = list(map(lambda x: x.get('href'),
                    soup.find('ol').find_all('a')))
    for i in range(1, len(linkList)+1):
        links[f'{i}'] = linkList[i-1]
    return links
