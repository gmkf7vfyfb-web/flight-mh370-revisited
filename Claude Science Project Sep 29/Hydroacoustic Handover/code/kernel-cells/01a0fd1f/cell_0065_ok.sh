cd rr; python - <<'EOF'
import json
rows=json.load(open('royer_table5.json'))
def sec(x):
    h,m,s=x.split(':'); return int(h)*3600+int(m)*60+float(s)
lab={3:('00:51:59','00:37:37'),4:('00:36:10','00:47:42'),7:('01:34:47',None),11:('01:34:49','01:19:01'),15:('01:29:56',None)}
for i,(h,sw) in lab.items():
    r=rows[str(i)]
    hm=sum(sec(r[c]) for c in ['H01W1','H01W2','H01W3'])/3
    out=f"event {i}: H01W map-minus-mean {sec(h)-hm:+.1f} s"
    if sw:
        v=[sec(r[c]) for c in ['SWAMS1','SWAMS2','SWAMS3'] if r[c]!='X']
        out+=f"; SWAMS map-minus-mean {sec(sw)-sum(v)/len(v):+.1f} s (range {sec(sw)-max(v):+.1f}..{sec(sw)-min(v):+.1f})"
    print(out)
print('range error for 16 s at 1.48 km/s:',16*1.48,'km')
EOF