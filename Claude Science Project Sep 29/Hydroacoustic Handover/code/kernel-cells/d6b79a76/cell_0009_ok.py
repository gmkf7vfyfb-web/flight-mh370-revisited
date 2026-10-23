r=host.query("SELECT id, body FROM memories WHERE id IN ('mem_70d248dc49c4','mem_5c5b944c0184','mem_d80705c112ca','mem_25bc19063233','mem_320b4bd369e9')")
for row in r['rows']: print(row[0], row[1]); print()
r=host.query("SELECT id, body FROM memories WHERE body LIKE '%joined-v2%' AND body LIKE '%run-j%' ORDER BY created_at DESC LIMIT 8")
for row in r['rows']: print(row[0], row[1]); print()
