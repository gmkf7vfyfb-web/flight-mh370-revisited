r = host.query("SELECT id, body FROM memories WHERE superseded_by IS NULL AND (body LIKE '%infrasound%' OR body LIKE '%Indonesia%' OR body LIKE '%OHASISBIO%' OR body LIKE '%Cocos%' OR body LIKE '%Royer%' OR body LIKE '%Blackman%')")
import json
open('handoff_mem.txt','w').write('\n--\n'.join(f"{a}: {b}" for a,b in r['rows']))
print(len(r['rows']))