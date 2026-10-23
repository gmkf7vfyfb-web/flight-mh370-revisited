cd src; curl -s --max-time 30 "https://api.crossref.org/works/10.1029/2023AV000915" -o aq.json; python -c "
import json;d=json.load(open('aq.json'))['message']; print(d.get('link')); print(d.get('license'))
for r in d.get('reference',[]):
    s=json.dumps(r).lower()
    if any(k in s for k in ['zenodo','figshare','pangaea','dryad','data','mendeley','doi.org/10.5281','10.6084']): print(r)
" | head -30