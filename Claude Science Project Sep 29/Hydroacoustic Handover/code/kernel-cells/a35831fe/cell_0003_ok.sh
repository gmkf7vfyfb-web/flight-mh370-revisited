ls; python - <<'E'
t=open('handoff_mem.txt').read().split('\n\n')
import re
k=[b for b in t if re.search(r'hydro|Royer|H01W|H08S|OHASIS|Kadri|coupling|Cape Leeuwin|Diego|ice|candidate signal|IMOS|Perth',b,re.I)]
print(len(k))
open('hydro_mem.txt','w').write('\n\n'.join(k))
E
wc -c hydro_mem.txt