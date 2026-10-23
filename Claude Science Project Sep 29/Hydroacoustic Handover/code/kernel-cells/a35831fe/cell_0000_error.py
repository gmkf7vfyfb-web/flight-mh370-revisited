rows = host.query("SELECT * FROM memories LIMIT 1")
print(rows[0].keys() if rows else rows)