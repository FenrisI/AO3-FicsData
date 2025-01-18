while findNext(ficLink) != None:
        
        print("....")
        FIC=s.get(site+ficLink)
        t=time.time()
        soup = BS(FIC.text, "html.parser")

        counts.append(chapterWords())
        ficLink = findNext(ficLink)
        print(time.time()-t)
diff = time.time() - start