r = host.artifacts(search="Acoustic publication coverage versus end of flight", limit=10)
for a in r["artifacts"]:
    print(a["filename"], a["id"], a["latest_version_id"], a.get("_score"))
r2 = host.artifacts(filename="publication", limit=20)
for a in r2["artifacts"]:
    print("F:", a["filename"], a["latest_version_id"])