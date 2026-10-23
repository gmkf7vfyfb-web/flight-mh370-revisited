cfg = rj["config"]
print("top-level config keys:", list(cfg.keys()))
fuel = cfg.get("fuel") or {}
print("\n=== fuel block ===")
for k in sorted(fuel): print(f"  {k} = {fuel[k]}")
