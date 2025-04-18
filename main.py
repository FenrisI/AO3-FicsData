from Ao3_ficData import *


if __name__ == "__main__":
    ses = requests.Session()
    ses.headers.update(HEADERS)
    ses.cookies.update(COOKIES)
    chapters = {}
    ficLink = "https://archiveofourown.org/works/58203763/chapters/148881631"

    res = ses.get(f"{SITE}/works/{getFicID(ficLink)}?view_full_work=true")
    print(getFicID(ficLink))
    print(res.status_code)
    soup = BS(res.text, "html.parser")

    fic(ses, ficLink)

    ses.close()
