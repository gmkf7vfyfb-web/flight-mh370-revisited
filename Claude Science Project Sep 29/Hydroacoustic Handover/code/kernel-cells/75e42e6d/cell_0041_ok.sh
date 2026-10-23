cd src; curl -s --max-time 30 "https://data.mendeley.com/public-api/datasets/nr4vt4h8gt/files?folder_id=root&version=4" -o mdl_files.json; curl -s --max-time 30 "https://data.mendeley.com/public-api/datasets/nr4vt4h8gt/folders/4" -o mdl_folders.json; python - <<'EOF'
import json
f=json.load(open('mdl_files.json'))
for x in f: print(x['filename'], x['content_details'].get('size'), x['content_details'].get('content_type'))
try:
    fo=json.load(open('mdl_folders.json')); print('folders:', [(z.get('name'),z.get('id')) for z in fo] if isinstance(fo,list) else fo)
except Exception as e: print('folders err', e, open('mdl_folders.json').read()[:200])
EOF