r = host.query("""
SELECT id, agent_name, status, input_tokens, output_tokens,
       round(CAST(input_tokens AS REAL)/NULLIF(output_tokens,0),0) AS reread,
       round(total_cost,1) AS cost,
       datetime(created_at/1000,'unixepoch') AS created,
       round((updated_at-created_at)/86400000.0,2) AS days_open
FROM frames
WHERE project_id='proj_9cc1a5a85f63' AND parent_frame_id IS NULL
ORDER BY created_at DESC""")
print(" | ".join(r["columns"]))
for x in r["rows"]: print(x)
