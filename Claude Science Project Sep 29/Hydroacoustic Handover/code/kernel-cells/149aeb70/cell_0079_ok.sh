cd "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/149aeb70-e4ae-4829-a477-5c291fc000a5" && python3 - <<'PY'
p="make_hydro_figs.py"; s=open(p).read()
s=s.replace("""ax.legend(handles=[Line2D([], [], ls="none", marker="o", ms=4, color="#1b3a6b", label="loud decile (top 10% peak power)")],
          loc="lower left", frameon=False, fontsize=6.5)""",
"""ax.legend(handles=[Line2D([], [], ls="none", marker="h", ms=6, color="0.62",
                          label="all 20,000 drawn impacts (grey hexagons, count on the bar)"),
                   Line2D([], [], ls="none", marker="o", ms=4, color="#1b3a6b",
                          label="loud decile (top 10% peak power)")],
          loc="lower left", frameon=False, fontsize=6.5)""")
open(p,"w").write(s); print("ok")
PY