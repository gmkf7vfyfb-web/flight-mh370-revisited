import json
rows = host.query("""
SELECT filename, id, latest_version_id FROM artifacts
WHERE lower(filename) LIKE '%eof%' OR lower(filename) LIKE '%end-of-flight%'
   OR lower(filename) LIKE '%terminal%' OR lower(filename) LIKE '%impact%'
   OR lower(filename) LIKE '%boeing%' OR lower(filename) LIKE '%brief%'
   OR lower(filename) LIKE '%architecture%'
ORDER BY filename
""")
for r in rows["rows"]: print(r)
