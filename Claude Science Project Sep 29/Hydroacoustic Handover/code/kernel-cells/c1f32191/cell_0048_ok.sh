cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j" && python - <<'EOF'
s=open("charts.py").read()
s=s.replace('''def footnotes(fig, plain, tech, y0=0.005):
    fig.text(0.01, y0 + 0.055, textwrap.fill("Plain-language note: " + plain, 230), fontsize=6, va="bottom", ha="left", color="#333333")
    fig.text(0.01, y0, textwrap.fill("Technical note: " + tech, 230), fontsize=6, va="bottom", ha="left", color="#333333")''',
'''def footnotes(fig, plain, tech, y0=0.005, width=215):
    t2 = textwrap.fill("Technical note: " + tech, width); n2 = t2.count("\\n") + 1
    h_in = fig.get_size_inches()[1]; line = 6 * 1.35 / 72 / h_in          # line height in figure fraction at 6 pt
    fig.text(0.01, y0, t2, fontsize=6, va="bottom", ha="left", color="#333333")
    fig.text(0.01, y0 + n2 * line + 0.012, textwrap.fill("Plain-language note: " + plain, width), fontsize=6, va="bottom", ha="left", color="#333333")''')
# evidence chart: taller, ND-only alone line
s=s.replace('''    fig, axes = plt.subplots(1, 4, figsize=(11.5, 3.9), sharey=True); fig.subplots_adjust(left=0.06, right=0.99, top=0.80, bottom=0.36, wspace=0.08)''',
'''    fig, axes = plt.subplots(1, 4, figsize=(11.5, 4.9), sharey=True); fig.subplots_adjust(left=0.06, right=0.99, top=0.83, bottom=0.42, wspace=0.08)
    nd = json.load(open(out / "nd_alone_1deg.json"))''')
s=s.replace('''        ax.step(mid[sel], alone[sel], where="mid", color=C_ALONE, lw=1.1, ls="--", label="hydroacoustics alone, flat prior along the arc")''',
'''        ax.step(mid[sel], alone[sel], where="mid", color=C_ALONE, lw=1.1, ls="--", label="hydroacoustics alone, flat prior along the arc")
        xb = np.array(nd["band_mid"]); yb = np.array(nd[f"{o}/p0.5"]) / 2.0     # 1-degree bands scaled to the 0.5-degree bin height
        ax.step(xb, yb, where="mid", color="#7a4a10", lw=0.8, ls="-.", label="hydroacoustics alone, non-detections only (1° bands)")''')
s=s.replace('''    h, l = axes[0].get_legend_handles_labels(); fig.legend(h, l, loc="upper left", bbox_to_anchor=(0.06, 0.985), ncol=2, fontsize=7)''',
'''    h, l = axes[0].get_legend_handles_labels(); fig.legend(h, l, loc="upper left", bbox_to_anchor=(0.06, 0.975), ncol=3, fontsize=6.5)''')
# limits chart
s=s.replace('''    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.0)); fig.subplots_adjust(left=0.06, right=0.99, top=0.84, bottom=0.36, wspace=0.22)''',
'''    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.0), gridspec_kw=dict(width_ratios=[1.25, 1])); fig.subplots_adjust(left=0.06, right=0.99, top=0.86, bottom=0.40, wspace=0.30)''')
s=s.replace('''    ax.axhline(0.05, color="#b03030", lw=0.8, ls="--"); ax.text(1.1e-4, 0.065, "95 % exclusion would need the curve to reach 0.05", fontsize=6, color="#b03030")''',
'''    ax.axhline(0.05, color="#b03030", lw=0.8, ls="--"); ax.text(1.3e-2, 0.07, "95 % exclusion needs 0.05", fontsize=6, color="#b03030", ha="right")''')
s=s.replace('''    ax.set_ylabel("Probability that none of the four recorders would have detected the impact")''','''    ax.set_ylabel("Probability that no recorder detects the impact")''')
s=s.replace('''    ax.set_title("a  Even at a coupling efficiency of 0.01, the recordings held miss the impact about 40 % of the time", loc="left", fontsize=7.5)
    ax.legend(loc="lower left", fontsize=6)''','''    ax.set_title("a  Even at a coupling efficiency of 0.01 the recordings held\\n    miss the impact about 40 % of the time", loc="left", fontsize=7.5)
    ax.legend(loc="lower left", fontsize=6, bbox_to_anchor=(0.0, 0.08))''')
s=s.replace('''    ax.set_yticks(y); ax.set_yticklabels([OPT[o] for o in sel.option]); ax.set_xscale("log")''','''    SHORT = {"D0": "00:19 held out", "D2": "BTO + BFO", "D3": "both BFOs (H2)", "D4": "both BFOs, offset (H1)"}
    ax.set_yticks(y); ax.set_yticklabels([SHORT[o] for o in sel.option]); ax.set_xscale("log")''')
s=s.replace('''    ax.set_title("b  The 95 % upper limit sits at the prior's edge: the non-detection constrains little", loc="left", fontsize=7.5)''',
'''    ax.set_title("b  The 95 % upper limit sits near the prior's own:\\n    the non-detection constrains little", loc="left", fontsize=7.5)''')
open("charts.py","w").write(s)
# reduce: write nd_alone_1deg.json (mean Pnd marg per 1-degree band, normalised over 41-20 S) 
r=open("reduce.py").read()
r=r.replace('''    fam, hol = families_and_holland(mx, norm)''','''    nd = {"band_mid": (R.LAT_BAND_EDGES_1DEG[:-1] + 0.5).tolist()}
    for j, key in enumerate(KEYS):
        P = mx[f"wPnd_{ALPHA_TAGS[R.ALPHA_PRIMARY]}"][j][1:22, :NG].mean(1); w = mx["sum_w"][j][1:22]
        with np.errstate(invalid="ignore", divide="ignore"):
            v = np.where(w > 1e-9 * w.sum(), P / w, 0.0)
        nd[key] = (v / v.sum()).tolist() if v.sum() > 0 else v.tolist()
    json.dump(nd, open(out / "nd_alone_1deg.json", "w"), indent=0)
    fam, hol = families_and_holland(mx, norm)''')
open("reduce.py","w").write(r); print("ok")
EOF
S=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated.staging && OMP_NUM_THREADS=1 python reduce.py $S /tmp/b11test 2>&1 | grep -v Warn | tail -1 && python charts.py /tmp/b11test /tmp/b11res test 2>&1 | grep -v Warn | tail -2 && cp /tmp/b11res/*.png charts_test/; tail -1 $S/driver.log; ls $S/_parts | wc -l