print(host.query("SELECT sql FROM sqlite_master WHERE name='frames'")["rows"][0][0][:900])
