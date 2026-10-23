import json
r = host.query("""SELECT id, agent_name, status, created_at, updated_at, substr(coalesce(title,''),1,80) t
FROM frames WHERE created_at > datetime('now','-3 days') ORDER BY created_at""")
for row in r[:80]: print(row)