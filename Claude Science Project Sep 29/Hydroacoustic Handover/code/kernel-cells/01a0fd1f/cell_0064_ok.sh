cd rr; python - <<'EOF'
import re
t=open('royer2016.txt').read()
p15=t[t.find('=== PAGE 15 ==='):t.find('=== PAGE 16 ===')]
cols=['MAD','NCRO','WKER','SSEIR','SWAMS1','SWAMS2','SWAMS3','H01W1','H01W2','H01W3']
rows={}
for line in p15.split('\n'):
    f=[x.strip() for x in line.split('\t') if x.strip()]
    if f and f[0].isdigit() and 1<=int(f[0])<=20 and len(f)>=12:
        idx=int(f[0]); vals=f[-10:]; rows[idx]=dict(zip(cols,vals))
print(len(rows))
def sites(r):
    s=set()
    for c,v in r.items():
        if v!='X': s.add('SWAMS' if c.startswith('SWAMS') else 'H01W' if c.startswith('H01W') else c)
    return s
for i in range(1,21):
    r=rows[i]; s=sites(r); print(i, len([v for v in r.values() if v!='X']), len(s), sorted(s))
def sec(x):
    h,m,s=x.split(':'); return int(h)*3600+int(m)*60+float(s)
# figure-map labels read from rendered pages (to the second)
fig={ 'Fig4 (A,3)':(3,{'MAD':'01:04:24','WKER':'00:42:04','SWAMS3':'00:37:37','H01W2':'00:51:59'}),
 'Fig5 (B,4)':(4,{'MAD':'01:07:34','SWAMS3':'00:47:42','H01W2':'00:36:10'}),
 'Fig6 (C1,7)':(7,{'MAD':'01:07:40','SSEIR':'01:11:15','NCRO':'01:26:24','H01W2':'01:34:47'}),
 'Fig7 (C2,11)':(11,{'NCRO':'01:31:35','SSEIR':'01:11:20','SWAMS3':'01:19:01','H01W2':'01:34:49'}),
 'Fig8 (D2,15)':(15,{'MAD':'01:45:23','SSEIR':'01:31:13','NCRO':'01:49:48','H01W2':'01:29:56'})}
for k,(i,d) in fig.items():
    out=[]
    for c,v in d.items():
        tv=rows[i][c] if c in rows[i] else 'X'
        if c=='SWAMS3' and rows[i]['SWAMS3']=='X': tv='X'
        out.append(f"{c}: map {v} vs table {tv} -> {'n/a' if tv=='X' else round(sec(v)-sec(tv),1)} s")
    print(k,'; '.join(out))
import json; json.dump(rows,open('royer_table5.json','w'))
EOF