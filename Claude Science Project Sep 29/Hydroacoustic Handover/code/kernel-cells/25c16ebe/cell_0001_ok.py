print(host.query("SELECT count(*) FROM artifacts")["rows"])
f = host.frames(max_results=60)
for fr in f["frames"]:
    print({k:v for k,v in fr.items() if k in ("frame_id","status","task","created_at","title","agent_name")})
