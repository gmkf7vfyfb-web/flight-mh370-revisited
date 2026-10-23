r = host.frames(max_results=60)
for f in r["frames"]:
    print(f["id"][:8], f["status"], f["agent_name"], "|", f["name"], "| updated", f["updated_at"], "| arts", f["artifact_count"])
