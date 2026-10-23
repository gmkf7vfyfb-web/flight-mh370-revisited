O=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated; python - <<'EOF'
p="/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated/README.txt"; s=open(p).read()
line="SUPERSEDED by run-j-gated-v2 (IMOS TL table): the columns here are on the OLD imos_tl_ramcorr_arc.csv table; use run-j-gated-v2 (imos_tl_ram_arc.csv).\n\n"
if not s.startswith("SUPERSEDED"): open(p,"w").write(line+s)
print(open(p).read()[:160])
EOF
cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j" && python - <<'EOF'
s=open("charts.py").read()
s=s.replace('''    sub = np.load(out / "subsample_merged.npz"); W = sub["W"][4]; lat = sub["lat"]; lg = sub["lnL_grid"][:, :len(R.ETA_GRID)].astype(float)
''','')
s=s.replace('''        m = (lat >= lo) & (lat < hi) & (W > 0)
        if m.sum() < 50: continue
        w = W[m] / W[m].sum()
        # non-detection probability per eta needs lnPnd; the subsample carries lnL (with matches) -- use the table's band values at the three tabulated eta instead
        row =''','''        row =''')
s=s.replace('''        if not len(rr) if False else False: pass
''','')
s=s.replace('''    fig.suptitle("At dive probability 0.5, adding the hydroacoustic result moves the end-of-flight latitude distribution by 0.1–0.3°;\\nthe bumps near 33–36°S come from two time-matched Portland candidates that are too loud to be the aircraft (amplitude-blind matching)", x=0.01, ha="left", y=0.998, fontsize=8.5)''',
'''    sh = [abs(ev[(ev.option == o) & (ev.p == 0.5) & (ev.alpha == 0.05) & (ev.receivers == "IMOS gated")].iloc[0].shift_median_deg) for o in R.OPTIONS]
    fig.suptitle(f"At dive probability 0.5, adding the hydroacoustic result moves the end-of-flight latitude distribution by {min(sh):.2f}–{max(sh):.2f}°;\\nthe bumps near 33–36°S come from two time-matched Portland candidates that are too loud to be the aircraft (amplitude-blind matching)", x=0.01, ha="left", y=0.998, fontsize=8.5)''')
s=s.replace('''    ax.set_title("a  Even at a coupling efficiency of 0.01 the recordings held\\n    miss the impact about 40 % of the time", loc="left", fontsize=7.5)''',
'''    ax.set_title(f"a  Even at a coupling efficiency of 0.01 the recordings held\\n    miss the impact about {100 * row['pnd_at_1e-2']:.0f} % of the time", loc="left", fontsize=7.5)''')
s=s.replace('''"(a) For impacts in each latitude band of the flight simulation, the chance that all four recorders would have missed the sound, against the share of impact energy that becomes sound. The recorders ran for 5 minutes in every 15 and only two of them cover each arrival, so even a loud impact is missed about 40 % of the time.''',
'''f"(a) For impacts in each latitude band of the flight simulation, the chance that all four recorders would have missed the sound, against the share of impact energy that becomes sound. The recorders ran for 5 minutes in every 15 and only two of them cover each arrival, so even a loud impact is missed about {100 * row['pnd_at_1e-2']:.0f} % of the time.''')
s=s.replace('''PREDICTIVE, NOT CALIBRATED; C1, C2; TL arc grid (IMOS RAM-corrected, G-TL1). Block 11 prereg 90d7181; {tag}.")''','''PREDICTIVE, NOT CALIBRATED; C1, C2; TL arc grid (IMOS: RAM along the grid, imos_tl_ram_arc.csv, amendment A4). Block 11 prereg 90d7181 + A4 e13a32e; {tag}.")''')
s=s.replace('''TL block 2 arc grid (41-20 S), E = contact KE''','''TL block 2 arc grid (41-20 S; IMOS: RAM along the grid, imos_tl_ram_arc.csv, amendment A4), E = contact KE''')
s=s.replace('''Block 11 prereg 90d7181; {tag}.")
    bad = check_overlaps(fig)
    for ext in ("png", "pdf"): fig.savefig(res / f"hydroacoustics-composition-run-j-evidence.{ext}")''','''Block 11 prereg 90d7181 + A4 e13a32e; {tag}.")
    bad = check_overlaps(fig)
    for ext in ("png", "pdf"): fig.savefig(res / f"hydroacoustics-composition-run-j-evidence.{ext}")''')
open("charts.py","w").write(s); import ast; ast.parse(s); print("ok")
EOF
grep -n "The recorders ran for 5 minutes" charts.py | head -2; grep -n 'footnotes(fig,$' charts.py | head; grep -n '^              "(a) For\|^              f"(a) For' charts.py