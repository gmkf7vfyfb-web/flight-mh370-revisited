
import json
out=[]
for term in ["Kadri", "airplane crash", "Remote hydroacoustic detection", "hydroacoustic pdf", "Scientific Reports"]:
    r = host.artifacts(search=term, limit=1000)
    for a in r['artifacts']:
        fn=a['filename']
        if fn.lower().endswith('.pdf') or 'kadri' in fn.lower() or 'airplane' in fn.lower():
            out.append((fn, a['id'], a.get('size_bytes'), a.get('content_type')))
out=sorted(set(out))
for o in out: print(o)
print(len(out))
# all PDFs in project
r = host.artifacts(content_type="application/pdf", limit=1000)
print("pdf count", r['count'])
for a in r['artifacts']:
    print(a['filename'], a['id'], a.get('size_bytes'))
