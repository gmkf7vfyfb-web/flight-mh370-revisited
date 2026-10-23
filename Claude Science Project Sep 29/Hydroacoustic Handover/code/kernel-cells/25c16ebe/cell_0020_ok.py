r = host.query("""
SELECT filename, a.latest_version_id, datetime(a.created_at/1000,'unixepoch') d
FROM artifacts a WHERE lower(filename) LIKE '%boeing%' OR lower(filename) LIKE '%calib%'
   OR lower(filename) LIKE '%6dof%' OR lower(filename) LIKE '%6-dof%' OR lower(filename) LIKE '%fit%'
ORDER BY a.created_at DESC LIMIT 40""")
for x in r["rows"]: print(x)
