cd prior/Blackman_2004_extracted_data; python3 -c "
import json,hashlib
d=json.load(open('SHA256SUMS.json')); print(type(d))
items=d.items() if isinstance(d,dict) else [(x.get('file') or x.get('path'),x.get('sha256')) for x in d]
for k,v in items:
    k2=k.split('/')[-1]
    try: print(k2, hashlib.sha256(open(k2,'rb').read()).hexdigest()==v)
    except Exception as e: print(k2,e)
"; cat blackman_extraction_manifest.json; head -3 *.csv | cut -c1-400