for q in ["Kadri collaboration package licensing data we can share",
          "Kadri package windows deliverables code test datasets"]:
    print("##", q)
    for a in host.artifacts(search=q, limit=8)["artifacts"]:
        print("  ", a["filename"], "|", a.get("size_bytes"), "|", a["latest_version_id"])
