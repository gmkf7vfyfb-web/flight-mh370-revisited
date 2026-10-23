a = host.artifacts(frame_id='a35831fe-107a-4961-bc9f-e6fd6d255601')
items = a if isinstance(a, list) else a.get('artifacts', a)
print(len(items))
for x in items[:80]:
    print(x.get('filename'), '|', str(x.get('version_id', x.get('latest_version_id','')))[:8], '|', x.get('size_bytes'))