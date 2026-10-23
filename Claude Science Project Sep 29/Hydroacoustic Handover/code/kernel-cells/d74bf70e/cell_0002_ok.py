r = host.artifacts(search="hydroacoustics master prompt brief", limit=15)
for x in r["artifacts"]:
    print(x["filename"], "|", x["latest_version_id"], "|", x.get("size_bytes"))
print("====")
r2 = host.artifacts(filename="hydro", limit=25)
for x in r2["artifacts"]:
    print(x["filename"], "|", x["latest_version_id"], "|", x.get("size_bytes"))
