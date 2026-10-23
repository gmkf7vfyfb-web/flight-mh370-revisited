
for q in ["ATSB operational search MH370","definition of underwater search areas","safety investigation report appendix","Boeing simulator cases end of flight"]:
    r = host.artifacts(search=q, limit=8)
    print("##", q, r["count"])
    for a in r["artifacts"][:8]:
        print("   ", a["filename"], a["content_type"], a.get("size_bytes"))
