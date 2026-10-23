
import datetime
r = host.query("""SELECT av.id AS vid, a.filename AS fn, av.size_bytes AS sz, av.created_at AS created, substr(av.checksum,1,10) AS ck
FROM artifact_versions av JOIN artifacts a ON a.id=av.artifact_id
WHERE (lower(a.filename) LIKE '%.pdf') AND (lower(a.filename) LIKE '%kadri%' OR lower(a.filename) LIKE '%s41598%' OR lower(a.filename) LIKE '%underwater_acoustic%' OR lower(a.filename) LIKE '%rewinding%' OR lower(a.filename) LIKE '%elasticity%' OR lower(a.filename) LIKE '%acoustic-gravity%' OR lower(a.filename) LIKE '%acoustic_gravity%' OR lower(a.filename) LIKE '%MOESM%')
ORDER BY a.filename, av.created_at""", limit=200)
print(r['row_count'])
for row in r['rows']:
    d = datetime.datetime.utcfromtimestamp(row[3]/1000).strftime('%Y-%m-%d %H:%M')
    print(row[0][:8], '|', row[1][:95], '|', row[2], '|', d, '|', row[4])
m = host.query("SELECT av.id, a.filename, av.created_at FROM artifact_versions av JOIN artifacts a ON a.id=av.artifact_id WHERE av.id LIKE '7e4d336f%' OR av.id LIKE '1dc5cd5c%' OR av.id LIKE '762d77c2%'")
for row in m['rows']: print(row[0][:8], row[1], datetime.datetime.utcfromtimestamp(row[2]/1000).strftime('%Y-%m-%d %H:%M UTC'))
