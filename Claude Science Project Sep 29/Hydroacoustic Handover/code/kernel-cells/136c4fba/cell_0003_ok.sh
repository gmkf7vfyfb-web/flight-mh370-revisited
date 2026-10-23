cd /tmp && python3 -c "
import os,json,urllib.request
req=urllib.request.Request('https://api.github.com/user/repos?per_page=100&sort=pushed',headers={'Authorization':'Bearer '+os.environ['GITHUB_TOKEN'],'Accept':'application/vnd.github+json'})
d=json.load(urllib.request.urlopen(req))
for r in d: print(r['full_name'], r['default_branch'], r['size'])
"