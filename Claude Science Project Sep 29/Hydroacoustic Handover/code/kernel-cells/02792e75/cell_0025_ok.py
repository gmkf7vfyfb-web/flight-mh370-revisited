trs={}
for u,ts,_ in cdx("jacc.gov.au/media/interviews/*",200):
    m=re.search(r"/april/(tr0\d\d)\.aspx$",u,re.I)
    if m:
        r=requests.get(f"http://web.archive.org/web/{ts}id_/{u}",timeout=60); t=strip(r.text)
        trs[m.group(1)]=(ts,u,t); open(f"src/jacc/{m.group(1)}.txt","w").write(f"http://web.archive.org/web/{ts}/{u}\n{t}")
for k,(ts,u,t) in sorted(trs.items()):
    tt=re.search(r"(?i)(transcript[^\n]{0,150})",t)
    print(k,ts,len(t),t.count("Haixun"),t.lower().count("white"), (tt.group(1)[:140] if tt else ""))