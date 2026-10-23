cd kh && python3 - <<'E'
s=open('figures.py').read()
s=s.replace("""OPT = {0: '00:19 data not used', 1: '00:19:29 range only', 2: '00:19:29 range and frequency', 3: 'Both 00:19 frequencies as recorded',
       4: 'Both 00:19 frequencies, shared start-up offset', 5: '00:19:29 frequency as recorded,\\n00:19:37 frequency with offset'}""",
"""OPT = {0: '00:19 data\\nnot used', 1: '00:19:29\\nrange only', 2: '00:19:29 range\\nand frequency', 3: 'Both 00:19 frequencies\\nas recorded',
       4: 'Both 00:19 frequencies,\\nshared start-up offset', 5: '00:19:29 frequency as recorded,\\n00:19:37 frequency with offset'}""")
s=s.replace("map_panel(axs[i, j], H, ess, OPT[d].replace(', ', ',\\n', 1) if i == 0 else '', ext)","map_panel(axs[i, j], H, ess, OPT[d] if i == 0 else '', ext); axs[i, j].set_xticks([100, 101, 102, 103])")
s=s.replace("fig.text(0.0, -0.20,","fig.text(0.0, -0.13,").replace("fig.text(0.0, -0.31,","fig.text(0.0, -0.22,")
open('figures.py','w').write(s)
E
echo ok