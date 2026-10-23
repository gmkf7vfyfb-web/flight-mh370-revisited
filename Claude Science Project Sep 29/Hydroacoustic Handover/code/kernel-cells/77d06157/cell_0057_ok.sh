cd gfx && python - <<'E'
s=open('charts_time.py').read()
s=s.replace('''ax.text(0.5 * (a + b), 0.0, "abcde"[k + (0 if rx == "H01W" else 3)], color="white"''','''ax.text(0.5 * (a + b), 0.0, "Fig. 9" + "abcde"[k + (0 if rx == "H01W" else 3)], color="white"''')
# chart6: union bands, layout, label position
s=s.replace('''        for k, (a, bb) in enumerate(PANELS[st]):
            lo_ = a - d / (R.C_SOFAR - 2 * R.C_SOFAR_SD); hi_ = bb - d / (R.C_SOFAR + 2 * R.C_SOFAR_SD)
            axb.fill_betweenx(lat, lo_, hi_, color=col, alpha=0.22, lw=0, label=lab + ", as impact time" if k == 0 else None)''','''        a, bb = PANELS[st][0][0], PANELS[st][-1][1]     # panels are contiguous
        lo_ = a - d / (R.C_SOFAR - 2 * R.C_SOFAR_SD); hi_ = bb - d / (R.C_SOFAR + 2 * R.C_SOFAR_SD)
        axb.fill_betweenx(lat, lo_, hi_, color=col, alpha=0.22, lw=0, label=lab + ", as impact time")''')
s=s.replace('''    axb.text(T0 + 47 * 60, -20.75, "impact-time 50 / 90 / 99 % (colours as in a)", fontsize=5.8, va="center")''','''    axb.text(T0 + 19 * 60, -20.75, "impact time 50 / 90 / 99 %\\n(colours as in a)", fontsize=5.8, va="center", ha="right")''')
s=s.replace('''    top = 0.92; hh = top - b - 0.17
    axa = fig.add_axes([0.06, b + 0.12 + 0.3 * hh, 0.4, 0.7 * hh]); axa2 = fig.add_axes([0.06, b + 0.10, 0.4, 0.24 * hh], sharex=axa)
    axb = fig.add_axes([0.56, b + 0.10, 0.42, hh])''','''    top = 0.92; hh = top - b - 0.17; hb_ = top - b - 0.25
    axa = fig.add_axes([0.06, b + 0.12 + 0.3 * hh, 0.4, 0.7 * hh]); axa2 = fig.add_axes([0.06, b + 0.10, 0.4, 0.24 * hh], sharex=axa)
    axb = fig.add_axes([0.56, b + 0.18, 0.42, hb_])''')
s=s.replace('''axb.legend(frameon=False, fontsize=6.2, loc="upper left", bbox_to_anchor=(0.0, -0.13), ncol=2)''','''axb.legend(frameon=False, fontsize=6.2, loc="upper left", bbox_to_anchor=(-0.05, -0.1), ncol=2)''')
open('charts_time.py','w').write(s)
E