r=host.query("SELECT sql FROM sqlite_master WHERE name='memories'")
print(r['rows'][0][0][:600])
