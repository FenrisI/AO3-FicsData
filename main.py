from Ao3_ficData import *


if __name__ == "__main__":
    ses = requests.Session()
    ses.headers.update(HEADERS)
    ses.cookies.update(COOKIES)
    chapters = {}
    ficLink = "https://archiveofourown.org/works/58203763/chapters/148881631"

    x = time.time()
    res = ses.get(f"{SITE}/works/{getFicID(ficLink)}?view_full_work=true")
    print(time.time()-x)

    print(getFicID(ficLink))
    print(res.status_code)
    soup = BS(res.text, "html.parser")

    x = time.time()
    fic(ses, ficLink)
    print(time.time()-x)

    ses.close()
