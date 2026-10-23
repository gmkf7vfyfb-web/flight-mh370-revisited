for q in ["Blackman_2004_extracted_data", "Blackman", "IMOS Curtin", "kadri", "Duncan Dall'Osto"]:
    r = host.artifacts(search=q, limit=6, project_id="all")
    print("##", q)
    for x in r["artifacts"]:
        if not x.get("_weak"): print("  ", x["filename"], "|", x["latest_version_id"], "|", x.get("size_bytes"), "|", x.get("project_id"))
