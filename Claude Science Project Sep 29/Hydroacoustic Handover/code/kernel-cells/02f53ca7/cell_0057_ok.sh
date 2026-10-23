cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"; python - <<'EOF'
s=open('tl_recal_block9_charts.py').read()
s=s.replace('label=f"path moved {d:+d} km (exploratory extension)" if d == 30 else None','label="path moved +30, +40, +50 km (exploratory extension)" if d == 30 else None')
s=s.replace('ax.set_xlabel("Lateral shift of the whole path at the ridge crossing (km; + = right of the forward direction)")','ax.set_xlabel("Sideways shift of the path at the ridge (km; + = right of the direction of travel)")')
s=s.replace('''ax.set_title("b  Shifting the path to the right deepens the sill and lowers the loss,\\n   but 24 dB of excess remains even when the ridge is cleared", fontsize=9, loc="left")''','''ax.set_title("b  Shifting the path right deepens the sill and lowers the loss,\\n   but about 24 dB of excess remains once the ridge is cleared", fontsize=9, loc="left")''')
s=s.replace('fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.6), gridspec_kw=dict(width_ratios=[1.5, 1]))','fig, axes = plt.subplots(1, 2, figsize=(12.0, 5.8), gridspec_kw=dict(width_ratios=[1.45, 1]))')
s=s.replace('fig.subplots_adjust(top=0.88, bottom=0.33, left=0.07, right=0.93, wspace=0.35)','fig.subplots_adjust(top=0.87, bottom=0.34, left=0.06, right=0.94, wspace=0.32)')
open('tl_recal_block9_charts.py','w').write(s)
EOF
W=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tlrecal; cat $W/ram.log | tail -3; ls $W/scratch_ram | head -3; date -u; uptime