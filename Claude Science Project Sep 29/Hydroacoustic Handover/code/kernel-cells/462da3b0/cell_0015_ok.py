for idx in (1560,1562,1564,1566,1568):
    r = host.frames(frame_id="d74bf70e-a424-46a9-8149-902d027e782a", offset=idx, max_results=2)
    for m in r["messages"]:
        t=json.dumps(m)
        if "search_windows" in t or "eof_shares" in t or "venv" in t:
            print(idx, t[:3500]); print("=====")