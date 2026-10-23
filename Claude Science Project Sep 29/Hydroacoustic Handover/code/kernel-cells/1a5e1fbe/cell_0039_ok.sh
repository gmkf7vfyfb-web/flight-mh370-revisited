cd pod; curl -s -m 30 -o items.json "https://www.arcgis.com/sharing/rest/search?q=Search_And_Rescue_Search_Area2014&f=json&num=10"; python3 - <<'E'
import json
d=json.load(open('items.json'))
print('total',d.get('total'))
for r in d.get('results',[]):
    print(r.get('id'),r.get('title'),r.get('owner'),r.get('type'),'| lic:',str(r.get('licenseInfo'))[:300],'| access:',str(r.get('accessInformation'))[:200],'| url',r.get('url'))
E
grep -o -i 'href="[^"]*"[^>]*>[^<]*\(Steel\|compressed\|Excel\|zip\)[^<]*' post.html | head; grep -o -i 'href="[^"]*\(dropbox\|duncansteel\|drive\.google\|\.zip\|\.xls\)[^"]*"' post.html | sort -u | head