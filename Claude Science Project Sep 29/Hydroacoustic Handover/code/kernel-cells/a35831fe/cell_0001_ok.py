rows = host.query("SELECT * FROM memories LIMIT 1")
print(type(rows)); print(str(rows)[:1500])