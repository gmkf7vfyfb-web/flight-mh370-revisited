export GIT_CONFIG_GLOBAL=/dev/null; URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"; git ls-remote --heads "$URL" | awk '{print $2}' | head -40; python - <<'EOF'
import os,requests,json
H={"Authorization":"Bearer "+os.environ["GITHUB_TOKEN"],"Accept":"application/vnd.github+json"}
R="https://api.github.com/repos/gmkf7vfyfb-web/flight-mh370-revisited"
br=[b['name'] for b in requests.get(R+"/branches?per_page=100",headers=H).json()]
hits={}
for b in br:
    t=requests.get(R+f"/git/trees/{b}?recursive=1",headers=H).json()
    paths=[x['path'] for x in t.get('tree',[]) if 'published-fig' in x['path'].lower() or ('kadri' in x['path'].lower() and x['path'].lower().endswith(('.png','.jpg','.jpeg','.tif','.tiff')) and 'Fig' in x['path'])]
    if paths: hits[b]=paths[:50]
    print(b, len(t.get('tree',[])), t.get('truncated'), len(paths))
json.dump(hits,open('gh_hits.json','w'),indent=1)
EOF
python -c "import json;h=json.load(open('gh_hits.json'));[print(b,p) for b,v in h.items() for p in v if 'pmc' not in p][:40]" | head -40