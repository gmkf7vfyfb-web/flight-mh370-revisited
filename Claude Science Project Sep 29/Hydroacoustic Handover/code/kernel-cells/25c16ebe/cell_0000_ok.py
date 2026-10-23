r = host.query("""
SELECT a.filename, av.content_type, av.size_bytes, a.latest_version_id, a.id,
       datetime(a.created_at/1000,'unixepoch') AS created
FROM artifacts a JOIN artifact_versions av ON a.latest_version_id = av.id
ORDER BY a.created_at DESC LIMIT 120
""")
for row in r["rows"]:
    print(row)
print(r["row_count"])
