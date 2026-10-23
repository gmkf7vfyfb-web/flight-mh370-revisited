r=host.query("SELECT id, body, source_frame_id FROM memories WHERE id IN ('mem_f710971254fe','mem_9785115f6343','mem_ad43e5f77e9d')")
for row in r['rows']: print(row[0], row[2], row[1]); print()
