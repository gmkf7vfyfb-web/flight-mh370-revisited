allp=[]
for off in (0,200,400):
    r=host.artifacts(content_type="application/pdf", limit=200, offset=off, project_id="all")
    allp+=r['artifacts']
print(len(allp))
names=sorted(set((a['filename'],a['latest_version_id'],a['size_bytes']) for a in allp if a['size_bytes']>300000))
for n in names: print(n)