r = host.query("""
SELECT a.id, a.filename, av.version_number, av.id AS version_id, av.size_bytes,
       datetime(av.created_at/1000,'unixepoch') AS created
FROM artifacts a JOIN artifact_versions av ON av.artifact_id = a.id
WHERE a.filename = 'end-of-flight.md'
ORDER BY av.version_number
""")
for x in r["rows"]: print(x)
print()
r2 = host.query("""
SELECT a.filename, a.latest_version_id, datetime(a.created_at/1000,'unixepoch') c
FROM artifacts a WHERE lower(a.filename) LIKE '%master%' OR lower(a.filename) LIKE '%prompt%'
ORDER BY a.created_at DESC LIMIT 25""")
for x in r2["rows"]: print(x)
