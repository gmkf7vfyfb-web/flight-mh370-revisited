import json
tm = json.load(open(host.artifact_path("db35b76b-dee0-4e8f-bdf9-498c34961977")))
print("h08s_template keys:", list(tm.keys()))
for k,v in tm.items():
    print(f"  {k}: {type(v).__name__} len={len(v) if hasattr(v,'__len__') else '-'}")
pe = json.load(open(host.artifact_path("2cd20e56-2b56-47e2-8043-30e5a5c39eca")))
for k,v in pe.items():
    print(f"pulse_energy.{k}: {type(v).__name__} len={len(v) if hasattr(v,'__len__') else '-'}")
hits = host.artifacts(search="H08S digitised envelope time series raw trace samples", limit=15)["artifacts"]
print("\nstore search:"); [print(" ", a["filename"], a.get("size_bytes")) for a in hits]
