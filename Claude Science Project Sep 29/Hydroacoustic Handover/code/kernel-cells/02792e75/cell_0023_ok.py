imgs=[x for x in im if not x[0].endswith("-tn.jpg") and x[2]=="image/jpeg" and re.search(r"mr_01[1-3]-",x[0])]
for u,ts,_ in imgs:
    fn="src/jacc/"+u.split("/")[-1]
    r=requests.get(f"http://web.archive.org/web/{ts}id_/{u}",timeout=60); open(fn,"wb").write(r.content); print(fn,len(r.content))