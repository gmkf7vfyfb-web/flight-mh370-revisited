cd ./.tmp; python3 - <<'EOF'
import json,urllib.request
for doi in ['10.1007/s00024-022-03117-6','10.1007/s00024-022-03090-0','10.1007/s00024-020-02445-9','10.1109/joe.2011.2154390','10.1121/10.0022761','10.1121/1.4976052']:
    try:
        r=json.load(urllib.request.urlopen(f'https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=title,abstract,year,isOpenAccess,openAccessPdf',timeout=30))
        print('##',doi,r.get('year'),r.get('isOpenAccess'),r.get('openAccessPdf')); print((r.get('abstract') or 'NO ABSTRACT')[:1500])
    except Exception as e: print('##',doi,'ERR',e)
EOF