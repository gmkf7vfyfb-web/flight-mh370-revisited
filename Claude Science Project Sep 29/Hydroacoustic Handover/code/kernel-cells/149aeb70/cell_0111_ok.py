r = host.artifacts(frame_id="d74bf70e-a424-46a9-8149-902d027e782a", limit=300)
for a in r["artifacts"]:
    f = a["filename"].lower()
    if any(k in f for k in ("trace","figure","fig","digit","h08s","series","envelope","shot","train","spl")):
        print(a["filename"], "|", a.get("size_bytes"), "|", a["latest_version_id"])
print("---- project-wide search")
for a in host.artifacts(search="digitised Kadri figure 9 trace H08S", limit=12)["artifacts"]:
    print(a["filename"], "|", a.get("size_bytes"), "|", a["latest_version_id"])
