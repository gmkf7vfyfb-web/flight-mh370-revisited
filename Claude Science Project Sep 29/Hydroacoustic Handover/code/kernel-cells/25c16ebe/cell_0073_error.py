r = host.query("""
SELECT frame_id, agent_name, status, datetime(created_at/1000,'unixepoch') c,
       datetime(updated_at/1000,'unixepoch') u
FROM frames WHERE project_id='proj_9cc1a5a85f63' AND parent_frame_id IS NULL
ORDER BY created_at DESC LIMIT 30""")
for x in r["rows"]: print(x)
