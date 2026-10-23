cd "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/149aeb70-e4ae-4829-a477-5c291fc000a5" && python3 - <<'PY'
import re
p="make_hydro_figs.py"; s=open(p).read()
# remove the now-duplicated tight_layout calls that preceded foot()
s=s.replace('fig1.tight_layout(rect=(0, 0.075, 1, 1))\n','')
s=s.replace('fig2.tight_layout(rect=(0, 0.12, 1, 1))\n','')
s=s.replace('fig3.tight_layout(rect=(0, 0.125, 1, 1))\n','')
s=s.replace('fig4.tight_layout(rect=(0, 0.16, 1, 1))\n','')
# coverage must ignore blocked paths
s=s.replace('for lg, d in LOGGERS.items():\n    arr = tim + gc_km(lat, lon, d["lat"], d["lon"]) / C_KMS\n    ncov += ((arr >= WIN[lg][0]) & (arr <= WIN[lg][1])).astype(int)',
            'for lg, d in LOGGERS.items():\n    if lg in BLOCKED:\n        continue\n    arr = tim + gc_km(lat, lon, d["lat"], d["lon"]) / C_KMS\n    ncov += ((arr >= WIN[lg][0]) & (arr <= WIN[lg][1])).astype(int)')
s=s.replace('cb.set_label("Loggers recording when the sound arrives", fontsize=6)',
            'cb.set_label("Unblocked loggers whose recording span\\ncovers the arrival", fontsize=6)')
s=s.replace('cb.ax.set_yticklabels(["none", "1", "2", "3 or more"], fontsize=6)',
            'cb.ax.set_yticklabels(["none", "1", "2", "3 or 4"], fontsize=6)')
s=s.replace('label="loud and short impacts"','label="loud and short impacts"')
# figure sizes: a little taller for footnotes
s=s.replace('figsize=(7.2, 5.0)','figsize=(7.2, 5.4)')
s=s.replace('figsize=(6.6, 3.5)','figsize=(6.8, 3.7)')
s=s.replace('figsize=(6.6, 4.2)','figsize=(6.8, 4.4)')
s=s.replace('figsize=(7.4, 3.8)','figsize=(7.6, 4.1)')
# map label placement
s=s.replace('ax.annotate(nm, (lo, la), (0, 7), textcoords="offset points", ha="center", fontsize=6.5, zorder=6)',
            'ax.annotate(nm, (lo, la), (-9, -2) if nm == "H01W" else ((4, 4) if nm == "H08N" else (6, -7)),\n                textcoords="offset points", ha="right" if nm == "H01W" else "left", fontsize=6.5, zorder=6)')
s=s.replace('"Perth Canyon (2 loggers)": (-31.86, 115.0, -9)','"Perth Canyon (2 loggers)": (-31.86, 115.0, 8)')
# fig2 annotation / threshold label placement
s=s.replace('ax.text(1000, len(order) - 0.35, " not estimable below 1,000", color="#d1495b", fontsize=6, va="center")',
            'ax.text(1000, len(order) - 1.25, " not estimable\\n below 1,000", color="#d1495b", fontsize=6, va="center")')
s=s.replace('textcoords="offset points", ha="right", fontsize=6, color="#1b3a6b")',
            'textcoords="offset points", ha="left", fontsize=6, color="#1b3a6b")')
s=s.replace('(-6, -10),\n                textcoords="offset points"','(7, -9),\n                textcoords="offset points"')
# fig3 label placement
s=s.replace('ax.text(TAU_SHORT * 0.88, 22, "short", fontsize=6, color="#d1495b", ha="right")',
            'ax.text(TAU_SHORT * 0.9, 0.38, "smoke-run cut", fontsize=6, color="#d1495b", ha="right", rotation=90, va="bottom")')
s=s.replace('ax.text(14, 0.9, "F-35A, 2019','ax.text(0.95, 1.9, "F-35A, 2019')
s=s.replace('fontsize=6, color="#a8631d", va="center", ha="right")','fontsize=6, color="#a8631d", va="bottom", ha="right")')
open(p,"w").write(s); print("patched")
PY