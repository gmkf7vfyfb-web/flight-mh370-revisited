cd "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/5e788282-a899-406d-be81-a794b69469f6/hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/metz_f35a"
python - <<'E'
s=open('charts.py').read()
s=s.replace('''ax.annotate(f"proposed value {S2['anchor_eta']:.2g}".replace("0.00226", "2.3 × 10⁻³"),''','''ax.annotate("proposed value " + sci(S2['anchor_eta']),''')
s=s.replace('''f"measured spectrum, 4-64 Hz only: {S2['routeB_eta_4_64_geomean']:.1e}".replace("e-03", " × 10⁻³")''','''"measured spectrum, 4-64 Hz only: " + sci(S2['routeB_eta_4_64_geomean'])''')
s=s.replace('''saved = []
''','''saved = []


def sci(v):
    e = int(np.floor(np.log10(v))); m = v / 10 ** e
    return f"{m:.1f} × 10" + str(e).replace("-", "⁻").translate(str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹"))
''')
open('charts.py','w').write(s)
E
grep -n "sci(" charts.py | head