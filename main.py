import requests
from gui import AO3AnalyticsApp

HEADERS = {'User-Agent': 'Fenris\'-AO3-Analytics-Tool',
           'DNT': '1',
           'Accept-Language': 'en-US,en:1=0.5',
           'Referer': 'https://archiveofourown.org/works'}
COOKIES = {'view_adult': 'true'}

def main():
        session = requests.session()
        session.headers.update(HEADERS)
        session.cookies.update(COOKIES)

        try:
            app = AO3AnalyticsApp(session=session)
            print("App started.")
            app.mainloop()
        except Exception as e:
            print(f"Error while starting the app: {e}")
        finally:
            session.close()

if __name__ == "__main__":
    main()