r = host.frames(frame_id="d74bf70e-a424-46a9-8149-902d027e782a", offset=1567, max_results=66)
for i,m in enumerate(r["messages"]):
    t=json.dumps(m)
    for mm in re.finditer(r"(seed-\d: \d+ rows[^\\]{0,60}|maximum resident[^\\]{0,40}|\d+\.\d+ real[^\\]{0,40}|\\\"validation\\\"[^}]{0,120})", t):
        print(1567+i, mm.group(0)[:200])
print(r["messages"][-1]["role"], json.dumps(r["messages"][-1])[:1500])