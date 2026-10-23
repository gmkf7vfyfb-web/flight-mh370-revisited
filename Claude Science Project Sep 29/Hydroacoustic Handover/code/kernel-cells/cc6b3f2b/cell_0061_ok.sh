cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/weak_signal"
python - <<'EOF'
s=open("charts.py").read()
# fig 1: one shared x label
s=s.replace('            if i == 1: ax.set_xlabel("Signal-to-noise ratio of the injected pulse (dB, peak 1 s band level over the background median)")\n','')
s=s.replace('    fig.legend(h[::-1], l[::-1], loc="upper center", ncol=4, fontsize=7, frameon=False, bbox_to_anchor=(0.5, 0.975))',
 '    fig.legend(h[::-1], l[::-1], loc="upper center", ncol=4, fontsize=7, frameon=False, bbox_to_anchor=(0.5, 0.975))\n    fig.supxlabel("Signal-to-noise ratio of the injected pulse (dB: peak 1 s band level over the background median, 5-40 Hz)", fontsize=8, y=0.215)')
s=s.replace('"Dispersion-aware matched filters detect injected impact pulses 6-9 dB fainter than the energy detectors at the same false-alarm rate (Perth Canyon logger 3376)"',
 '"Matched filters built on the dispersed arrival shape detect injected impact pulses 6-9 dB fainter than the energy detectors\\nat the same false-alarm rate (Perth Canyon logger 3376; the test pulses share the filters\' propagation model, so this is their best case)"')
s=s.replace('fig.subplots_adjust(top=0.86, bottom=0.2, left=0.06, right=0.99, hspace=0.3, wspace=0.08)','fig.subplots_adjust(top=0.85, bottom=0.25, left=0.06, right=0.99, hspace=0.3, wspace=0.08)')
# fig 2
s=s.replace('        ax.set_ylabel("plotted\\npressure (Pa)", fontsize=7)','        if col == 0: ax.set_ylabel("plotted\\npressure (Pa)", fontsize=7)')
s=s.replace('            ax.text((ta + tb) / 2, ax.get_ylim()[1] * 0.85 if ax.get_ylim()[1] else 0.8, name.replace("poster (a) ", "").replace("time ", "time\\n"), fontsize=6, ha="center", va="top")',
 '            ax.text((ta + tb) / 2, 1.02, name.replace("poster (a) ", "").replace(" time ", " "), fontsize=6, ha="center", va="bottom", transform=ax.get_xaxis_transform())')
s=s.replace('"On the digitised H01W traces, no method\'s statistic passes p = 0.05 inside the author\'s boxes except the envelope matched filter at the text time 00:52:03 (p = 0.05); the panel (a) boxes stay above p = 0.08"',
 '"On the digitised H01W traces only the envelope matched filter reaches p = 0.05 inside an author\'s box (text time 00:52:03);\\nthe four panel (a) boxes stay above p = 0.08 for every method"')
s=s.replace('fig.subplots_adjust(top=0.95, bottom=0.14, left=0.06, right=0.99, hspace=0.25, wspace=0.08)','fig.subplots_adjust(top=0.93, bottom=0.14, left=0.06, right=0.99, hspace=0.35, wspace=0.08)')
# fig 3
s=s.replace('''        ax.set_title(f"H08S panel ({pnl}), {pd.Timestamp('2014-03-08T01:00:00Z').strftime('%H:%M') if pnl == 'd' else '01:10'} UTC: {int(row.n_shots)} shots at {row.cadence_s:.2f} s; template subtraction {row.c1_reduction_db_whole:+.1f} dB, with gating {row.c1c2_reduction_db:+.1f} dB", fontsize=8, loc="left")''',
 '''        ax.set_title(f"H08S panel ({pnl}), {'01:00' if pnl == 'd' else '01:10'} UTC: {int(row.n_shots)} shots every {row.cadence_s:.2f} s;\\nresidual energy {row.c1_reduction_db_whole:+.1f} dB after subtraction, {row.c1c2_reduction_db:+.1f} dB with gating", fontsize=8, loc="left")''')
s=s.replace('        if col == 0: ax.legend(fontsize=6.5, frameon=False, loc="lower left", ncol=3)\n','        if col == 0: ax.legend(fontsize=6.5, frameon=False, loc="upper center", ncol=3, bbox_to_anchor=(1.05, -0.12))\n')
s=s.replace('"Airgun shot suppression on the digitised H08S traces lowers the residual energy by 5-8 dB and cuts chance coincidences from about 0.5 to 0.1-0.2; an added arrival 4 dB below the shots is still recovered"',
 '"Airgun shot suppression on the digitised H08S traces lowers the residual energy by 5-8 dB and cuts chance coincidences\\nfrom about 0.5 to 0.1-0.2 per trial; an added long-range arrival 4 dB below the shots is still recovered"')
s=s.replace('fig = plt.figure(figsize=(12, 8.2)); gs = fig.add_gridspec(3, 2, height_ratios=[1.2, 1.2, 1.1], hspace=0.45, wspace=0.25)','fig = plt.figure(figsize=(12, 9)); gs = fig.add_gridspec(3, 2, height_ratios=[1.2, 1.2, 1.1], hspace=0.6, wspace=0.25)')
s=s.replace('fig.subplots_adjust(top=0.94, bottom=0.14, left=0.07, right=0.99)\n    for ext in ("png", "pdf"):\n        fig.savefig(res / f"hydroacoustics-weak-signal-h08s','fig.subplots_adjust(top=0.92, bottom=0.13, left=0.07, right=0.99)\n    for ext in ("png", "pdf"):\n        fig.savefig(res / f"hydroacoustics-weak-signal-h08s')
open("charts.py","w").write(s)
EOF
WS=$(cd ../../../../../../..; pwd); python charts.py "$WS/out" "$WS/out/figs" 2>&1 | grep -v Warning | tail -2