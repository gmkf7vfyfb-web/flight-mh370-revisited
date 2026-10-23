
rows = host.query("SELECT av.id AS vid, av.artifact_id, av.version_number, av.created_at, substr(av.checksum,1,12) AS ck, av.storage_path, a.filename FROM artifact_versions av JOIN artifacts a ON a.id=av.artifact_id WHERE av.id LIKE '7e4d336f%' OR av.checksum LIKE '652d200a%' OR a.filename LIKE '%s00024%' OR a.filename LIKE '%Metz%' ORDER BY av.created_at")
print(len(rows))
for r in rows: print(r)
