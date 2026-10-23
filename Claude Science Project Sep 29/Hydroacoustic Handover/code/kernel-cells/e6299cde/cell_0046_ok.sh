cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/searches_run_j"
python - <<'EOF'
s=open('charts.py').read()
s=s.replace('''def foot(fig, plain, tech):
    fig.text(0.01, 0.045, plain, fontsize=6, ha="left", va="bottom", wrap=True, color="0.25")
    fig.text(0.01, 0.005, tech, fontsize=5.2, ha="left", va="bottom", wrap=True, color="0.35")''','''def foot(fig, plain, tech, y1=0.075):
    fig.text(0.01, y1, plain, fontsize=6, ha="left", va="bottom", wrap=True, color="0.25")
    fig.text(0.01, 0.005, tech, fontsize=5.2, ha="left", va="bottom", wrap=True, color="0.35")''')
s=s.replace('''fig, ax = plt.subplots(figsize=(11, 7.4)); fig.subplots_adjust(left=0.13, right=0.99, top=0.9, bottom=0.2)''','''fig, ax = plt.subplots(figsize=(11, 8.2)); fig.subplots_adjust(left=0.13, right=0.99, top=0.84, bottom=0.2)''')
s=s.replace('''    ax.set_title("Candidate rows at every receiver sit inside the predicted arrival windows, at the rate chance predicts; none is a detection", loc="left")''','''    ax.set_title("Candidate rows at every receiver, at about the rate chance predicts on other days; none is a detection", loc="left", y=1.19)''')
s=s.replace('''    ax.legend(handles=h, loc="upper center", bbox_to_anchor=(0.5, 1.0), ncol=3, frameon=False, fontsize=6.5)
    ax.text(x0 + 60, len(RX) - 0.5, "rows per receiver: upper = matched filter, middle = energy ratio, lower = band energy", fontsize=6, color="0.3", va="bottom")''','''    ax.legend(handles=h, loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=3, frameon=False, fontsize=6.5)
    ax.text(x1 - 60, -0.55, "rows per receiver: upper = matched filter, middle = energy ratio, lower = band energy", fontsize=6, color="0.3", va="bottom", ha="right")''')
s=s.replace('''fig, ax = plt.subplots(figsize=(9, 5.6)); fig.subplots_adjust(left=0.1, right=0.98, top=0.88, bottom=0.25)''','''fig, ax = plt.subplots(figsize=(9, 6.4)); fig.subplots_adjust(left=0.1, right=0.98, top=0.8, bottom=0.26)''')
s=s.replace('''    ax.set_title("Kadri's Table 1: the rows that point at the core region arrive too early; the rows in the time window point north of it", loc="left")''','''    ax.set_title("Kadri's Table 1: two rows fit both the arrival window and the predicted bearing; the 306° candidate is uninformative in bearing", loc="left", y=1.22)''')
s=s.replace('''    ax.legend(handles=h, loc="upper center", bbox_to_anchor=(0.5, 1.0), ncol=3, frameon=False, fontsize=6.3)
    foot(fig, "(i) What the chart shows: each dot is one of the 19 signals in Kadri's Table 1 (time and direction at Cape Leeuwin). The blue band is the direction in which the aircraft is predicted to lie. "
              "The yellow band is the time span in which its sound would arrive. A dot is credible only if it is inside both. The dots inside the blue band arrive too early for an impact after 00:19:29 (X); the dots in the time span point further north. "
              "The 306° row is uninformative on this impact set, not disfavoured as on the earlier stand-in.",''','''    ax.legend(handles=h, loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=3, frameon=False, fontsize=6.3)
    foot(fig, "(i) What the chart shows: each dot is one of the 19 signals in Kadri's Table 1 (time and direction at Cape Leeuwin). The blue band is the direction in which the aircraft is predicted to lie. "
              "The yellow band is the time span in which its sound would arrive. A dot is credible only if it is inside both. Three dots inside the blue band arrive too early for an impact after 00:19:29 (X); two (00:49:58, 00:53:31) fit both; "
              "the rest point further north. The 306° row is uninformative on this impact set, not disfavoured as on the earlier stand-in.", y1=0.085)''')
open('charts.py','w').write(s)
EOF
python charts.py /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches "$PWD/../../../../../../../repo/Claude Science Project Sep 29/results" 2>&1 | tail -1