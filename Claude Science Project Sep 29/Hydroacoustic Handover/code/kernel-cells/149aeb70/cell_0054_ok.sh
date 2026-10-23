cd "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/149aeb70-e4ae-4829-a477-5c291fc000a5" && python3 - <<'PY'
p="make_hydro_figs.py"; s=open(p).read()
s=s.replace("def foot(fig, ste, tech):","def foot(fig, ste, tech, use_tight=True):")
s=s.replace("""    bottom = len(lines) * lh + 0.018
    fig.tight_layout(rect=(0, bottom, 1, 1))""",
"""    bottom = len(lines) * lh + 0.018
    if use_tight:
        fig.tight_layout(rect=(0, bottom, 1, 1))
    else:
        fig.subplots_adjust(bottom=bottom + 0.13, top=0.90, left=0.135, right=0.985)""")
s=s.replace('axb.set_xlim(0, 18); axb.legend(loc="lower right", frameon=False, fontsize=6)',
            'axb.set_xlim(0, 19); axb.legend(loc="upper left", frameon=False, fontsize=6)')
s=s.replace('''foot(fig4,
     "Plain: panel a''','''foot(fig4,
     "Plain: panel a'''.replace("foot(fig4,","foot(fig4,"))
s=s.replace('''     "the same impact time.")
fig4.savefig''','''     "the same impact time.", use_tight=False)
fig4.savefig''')
open(p,"w").write(s); print("ok")
PY