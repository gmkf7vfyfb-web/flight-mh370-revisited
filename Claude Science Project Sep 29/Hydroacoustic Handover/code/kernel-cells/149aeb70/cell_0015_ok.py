r = host.artifacts(search="run I impacts terminal ess per option", limit=25)
for a in r["artifacts"]:
    print(a["filename"], "|", a.get("size_bytes"), "|", a["latest_version_id"][:8], "|", str(a.get("created_at"))[:19])
print("---")
r2 = host.artifacts(filename="run.json", limit=15)
for a in r2["artifacts"]:
    print(a["filename"], a.get("size_bytes"), a["latest_version_id"][:8], str(a.get("created_at"))[:19])
