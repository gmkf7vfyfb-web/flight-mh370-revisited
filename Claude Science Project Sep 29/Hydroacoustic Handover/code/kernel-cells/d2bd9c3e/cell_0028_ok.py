for pat in ["impact-time densities per option", "Fig. 9 windows", "coverage versus"]:
    rr = host.frames(pattern=pat, max_results=8, project_id="all")
    print(pat, rr["total_matches"])
    for m in rr["matches"][:8]:
        print("  ", m["frame_id"][:8], m["name"][:60], "|", str(m.get("snippets"))[:600])