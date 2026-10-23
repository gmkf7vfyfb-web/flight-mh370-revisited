cd /Users/pete/Downloads/mh370-exchange/end-of-flight && python3 - <<'PY'
import json
for r in ["run-i","run-i-dive","run-i-c2aim"]:
    try:
        d=json.load(open(f"{r}/next-i-free/seed-1/run.json"))
    except FileNotFoundError:
        d=json.load(open(f"{r}/next-i-waypoints/seed-1/run.json"))
    c=d["config"]; print("="*20, r, "| source_run:", d.get("source_run"))
    print("  config keys:", list(c.keys()))
    s=json.dumps(c)
    print("  len", len(s)); print("  ", s[:1200])
PY