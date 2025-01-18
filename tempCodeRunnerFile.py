def get(ficLink):
    FIC = s.get(site+ficLink)
    while FIC.ok == False:

            if FIC.status_code in [400,401,402,403,404,405] :
                break
            else:
                print("Retrying...")
                FIC=s.get(site+ficLink)
    return FIC