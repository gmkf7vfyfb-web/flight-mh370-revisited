for i in [401,402,403,404,408]:
    t=doc[i].get_text()
    print('=====PDF page',i+1); print(t[:4000])