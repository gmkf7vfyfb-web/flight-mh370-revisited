
r = host.query("SELECT av.id AS vid, av.artifact_id AS aid, av.version_number AS vn, av.created_at AS created, substr(av.checksum,1,12) AS ck, av.storage_path AS sp, a.filename AS fn FROM artifact_versions av JOIN artifacts a ON a.id=av.artifact_id WHERE av.id LIKE '7e4d336f%' OR av.checksum LIKE '652d200a%' OR a.filename LIKE '%s00024%' OR a.filename LIKE '%Metz%' ORDER BY av.created_at")
print(r['columns'], r['row_count'])
for row in r['rows']: print(row)
for fid in ['7adf9568','02f53ca7']:
    x = host.frames(frame_id=fid, include_tool_results=False, max_results=1)
    import re, json
    t = x['input'] if isinstance(x['input'],str) else json.dumps(x['input'])
    i = t.find('YOUR BLOCK')
    print('###',fid, re.sub(r'\s+',' ',t[i:i+900]))
