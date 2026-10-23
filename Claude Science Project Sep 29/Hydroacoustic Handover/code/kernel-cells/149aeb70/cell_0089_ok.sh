cd "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/149aeb70-e4ae-4829-a477-5c291fc000a5" && python3 - <<'PY'
p="make_run_compare_fig.py"; s=open(p).read()
s=s.replace('    ax.scatter(d["tau"][mid], d["en"][mid], s=5, color="#e8903a", lw=0, alpha=0.7, zorder=3)\n    ax.scatter(d["tau"][loud], d["en"][loud], s=4, color="#1b3a6b", lw=0, alpha=0.5, zorder=2)',
            '    ax.scatter(d["tau"][mid], d["en"][mid], s=2.5, color="#e8903a", lw=0, alpha=0.55, zorder=2)\n    ax.scatter(d["tau"][loud], d["en"][loud], s=3, color="#1b3a6b", lw=0, alpha=0.55, zorder=3)')
s=s.replace('cb = fig.colorbar(hb, ax=axes, shrink=0.8, pad=0.012); cb.set_label("impacts per cell (log scale)", fontsize=6)\n','')
s=s.replace('fig.subplots_adjust(bottom=bottom + 0.14, top=0.86, left=0.085, right=0.88)',
            'fig.subplots_adjust(bottom=bottom + 0.14, top=0.84, left=0.085, right=0.885)\n'
            'pos = axes[1].get_position()\n'
            'cax = fig.add_axes([0.905, pos.y0, 0.016, pos.height])\n'
            'cb = fig.colorbar(hb, cax=cax); cb.set_label("impacts per cell (log scale)", fontsize=6)')
open(p,"w").write(s); print("ok")
PY