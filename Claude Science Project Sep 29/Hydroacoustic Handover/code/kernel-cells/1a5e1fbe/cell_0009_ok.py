for i in range(216,226):
    t=doc[i].get_text()
    if re.search(r'POD|Coverage|Fatigue|debris',t):
        print('=====PDF page',i+1); print(re.sub(r'\n\s*\n','\n',t)[:3500])