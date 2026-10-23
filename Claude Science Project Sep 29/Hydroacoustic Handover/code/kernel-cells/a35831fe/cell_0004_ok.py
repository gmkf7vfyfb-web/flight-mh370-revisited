cut = int((time.time()-1.6*86400)*1000)
r = host.query(f"SELECT id, evidence, updated_at, source_frame_id, body FROM memories WHERE updated_at > {cut} AND superseded_by IS NULL ORDER BY updated_at")
print(r['row_count'])
with open('mem_recent.txt','w') as f:
    for row in r['rows']:
        f.write(f"[{time.strftime('%m-%d %H:%M', time.localtime(row[2]/1000))}] [{row[1]}] {row[0]} src={row[3][:8] if row[3] else None}\n{row[4]}\n\n")
print(time.strftime('%m-%d %H:%M', time.localtime()))