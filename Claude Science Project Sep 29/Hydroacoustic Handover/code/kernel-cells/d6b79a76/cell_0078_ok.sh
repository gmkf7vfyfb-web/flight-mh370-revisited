cd kh && python3 - <<'E'
s=open('figures.py').read()
s=s.replace("""    ax.axhline(0, color='0.5', lw=0.6); ax.axhline(np.log(1 / 18), color='0.5', lw=0.6, ls=':')
    ax.text(5.45, np.log(1 / 18) + 0.2, 'one chance arrival\\n(no rate) gives +2.89', fontsize=6, ha='right', va='bottom', color='0.35')""","""    ax.axhline(0, color='0.5', lw=0.6)""")
s=s.replace("'The run J flight posterior disfavours the sound as the impact, by ln B of about -4 to -7'","'ln Bayes factor is below 0 under every 00:19 treatment and both arrival readings'")
s=s.replace("Bars: per-seed min-max over run-j-waypoints seeds.","Sensitivity: one chance arrival without the 18-transient rate adds ln 18 = +2.89 to every value. Bars: per-seed min-max over run-j-waypoints seeds.")
open('figures.py','w').write(s)
E
mkdir -p fig; grep -c "ln 18" figures.py