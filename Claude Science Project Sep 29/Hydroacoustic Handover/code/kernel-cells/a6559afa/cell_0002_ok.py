q = host.query("SELECT sql FROM sqlite_master WHERE name IN ('frames','memories')")
print(type(q), str(q)[:2500])