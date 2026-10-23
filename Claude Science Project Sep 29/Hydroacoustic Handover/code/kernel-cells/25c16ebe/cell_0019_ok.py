import subprocess
free_cols=[c.strip() for c in open(f"{R}/next-i-free/seed-1/COLUMNS.txt") if c.strip()]
print("waypoints cols", len(cols), "free cols", len(free_cols))
print("in free not waypoints:", [c for c in free_cols if c not in ci])
print("in waypoints not free:", [c for c in cols if c not in set(free_cols)])
for nm,vid in [("boeing-table3-table4-reproduction.csv","37a1cdda-a2bb-4cc2-8439-fc60f2f4c195"),
               ("public-model-boeing-items.csv","da856e06-2149-4c94-9544-ff54c0e15542")]:
    t=open(host.artifact_path(vid),encoding="utf-8",errors="replace").read()
    print(f"\n===== {nm} =====\n{t[:3000]}")
