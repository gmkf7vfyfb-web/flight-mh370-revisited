r = host.artifacts(search="hydroacoustics master prompt RUN-STATE inbox", limit=40)
for a in r["artifacts"]:
    print(a["filename"], "|", a["latest_version_id"], "|", a.get("size_bytes"))
