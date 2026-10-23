cd rr; python - <<'EOF'
import re
t=open('mis2014.txt').read()
i=t.find('Configuration des mouillages'); i=t.find('Configuration des mouillages',i+100)
print(t[i:i+3500])
print('=====')
for k in ['autonomie','batterie','lest','largueur','flottab','Sercel','HTI','Persistor','échantillonn','240']:
    for m in re.finditer(k,t):
        s=t[max(0,m.start()-200):m.start()+250].replace('\n',' ')
        print(k,'::',s); break
EOF