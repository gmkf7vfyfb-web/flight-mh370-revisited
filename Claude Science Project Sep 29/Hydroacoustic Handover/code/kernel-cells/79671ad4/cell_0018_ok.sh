cd src; python -c "
import re
t=open('dk100.txt').read().split('=====PAGE=====')
print(len(t))
for i,x in enumerate(t):
  for kw in ['yards','Radiation','160.5','detected','April 13']:
    for m in re.finditer(re.escape(kw),x): print(i+1,kw,repr(re.sub(r'\s+',' ',x[max(0,m.start()-300):m.start()+300])))
" | head -30