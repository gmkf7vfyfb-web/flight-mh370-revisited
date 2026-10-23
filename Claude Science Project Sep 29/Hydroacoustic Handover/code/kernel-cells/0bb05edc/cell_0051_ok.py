
for r in srows:
    a=r['access_note'].strip()
    if a:
        print(r['id'],'|',r['citation'][:70],'|',r['url'][:50],'|',a[:170])
