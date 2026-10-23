cd "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/149aeb70-e4ae-4829-a477-5c291fc000a5" && python3 - <<'PY'
p="make_h08s_fig.py"; s=open(p).read()
s=s.replace('ax1.text(END - 25, -5.6, "digitised record ends 01:18:29", ha="right", fontsize=6.2, color="0.3")',
            'ax2.text(END - 18, -1.9, "digitised record ends 01:18:29", ha="right", fontsize=6.2, color="0.3",\n'
            '         rotation=90, va="bottom")')
s=s.replace('''ax2.annotate("01:19:21, the other candidate arrival, is 52 s past the end of the digitised panel",
             (END, 3.4), (-10, 0), textcoords="offset points", ha="right", fontsize=6.2, color="0.3")''',
            '''ax2.text(4800, -2.45, "01:19:21, the other candidate arrival, is 52 s past the end of the panel",
         ha="right", va="bottom", fontsize=6.2, color="0.3")''')
s=s.replace('''           loc="lower left", frameon=False, fontsize=6, ncol=3, handletextpad=0.4, columnspacing=1.0)''',
            '''           loc="lower left", bbox_to_anchor=(0.0, 1.06), frameon=False, fontsize=6, ncol=3,
           handletextpad=0.4, columnspacing=1.4)''')
s=s.replace('ax1.set_title("The only anomalies in the digitised record sit just before the search stopped", loc="left")',
            'ax1.set_title("The only anomalies in the digitised record sit just before the search stopped", loc="left", pad=22)')
s=s.replace('fig.subplots_adjust(bottom=bottom + 0.11, top=0.92, left=0.115, right=0.985)',
            'fig.subplots_adjust(bottom=bottom + 0.11, top=0.875, left=0.115, right=0.985)')
s=s.replace('(6, -16),\n             textcoords="offset points", fontsize=6.2, color="#a8313f"',
            '(8, -6),\n             textcoords="offset points", fontsize=6.2, color="#a8313f"')
open(p,"w").write(s); print("ok")
PY