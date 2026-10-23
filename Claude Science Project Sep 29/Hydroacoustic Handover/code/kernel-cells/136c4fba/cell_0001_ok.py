for q in ["hydroacoustics master prompt", "RUN-STATE", "HYDROACOUSTICS inbox", "kadri collaboration package"]:
    r = host.artifacts(search=q, limit=10)
    print("==", q, r["count"])
    for a in r["artifacts"]:
        print("  ", a["filename"], a["latest_version_id"])
