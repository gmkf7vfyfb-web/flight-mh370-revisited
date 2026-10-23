cd gfx && python - <<'E'
s=open('charts_levels.py').read()
a=s.index('    b = need_bottom(fig, plain, tech)\n    top = 0.905; gap = 0.06')
bq=s.index('    norm = mcolors.Normalize(-30, 20)')
s=s[:a]+'''    b = need_bottom(fig, plain, tech)
    top = 0.90; mh = 0.25; wd = 0.205
    pos = [[0.055 + c * 0.228, top - mh, wd, mh] for c in range(4)]
    pos_e = [0.17, b + 0.085, 0.32, top - mh - 0.11 - b - 0.085]; pos_f = [0.64, b + 0.085, 0.30, pos_e[3]]
'''+s[bq:]
s=s.replace('fig = plt.figure(figsize=(13.5, 10.2))\n    plain = ("Each dot is one likely place','fig = plt.figure(figsize=(15, 9.0))\n    plain = ("Each dot is one likely place')
s=s.replace('ax.scatter(z["lon"][o], z["lat"][o], c=s[o], s=2.2, cmap=cmap, norm=norm, lw=0, alpha=0.85, rasterized=True)','ax.scatter(z["lon"][o], z["lat"][o], c=s[o], s=3.0, cmap=cmap, norm=norm, lw=0, alpha=1.0, rasterized=True)')
s=s.replace('ax.set_xlabel("Longitude (°E)"); ax.set_ylabel("Latitude (°)" if k in (0, 3) else "")','ax.set_xlabel("Longitude (°E)"); ax.set_ylabel("Latitude" if k == 0 else "")\n        if k > 0: ax.set_yticklabels([])')
s=s.replace('''        ax.set_yticks([-40, -35, -30, -25, -20]); ax.set_yticklabels(["40°S", "35°S", "30°S", "25°S", "20°S"])''','''        ax.set_yticks([-40, -35, -30, -25, -20]); ax.set_yticklabels(["40°S", "35°S", "30°S", "25°S", "20°S"] if k == 0 else [])''')
s=s.replace('''    cax = fig.add_axes([pos[2][0] + wd + 0.008, pos[2][1] + 0.1 * hgt, 0.009, 0.8 * hgt])''','''    cax = fig.add_axes([pos[3][0] + wd + 0.012, pos[3][1] + 0.05 * mh, 0.008, 0.9 * mh])''')
s=s.replace('''    for thr, lab in ((7, "matched filter"), (15, "baseline")): cb.ax.axhline(thr, color="w", lw=1.2)''','''    for thr, lab in ((7, "matched\\nfilter"), (15, "baseline")): cb.ax.axhline(thr, color="w", lw=1.2); cb.ax.text(-0.6, thr, lab, fontsize=5.5, ha="right", va="center", transform=cb.ax.get_yaxis_transform())''')
s=s.replace('ax = fig.add_axes([pos[4][0] + 0.03, pos[4][1], wd - 0.03, hgt]); opts','ax = fig.add_axes(pos_e); opts')
s=s.replace('ax = fig.add_axes([pos[5][0] - 0.02, pos[5][1], wd + 0.02, hgt])','ax = fig.add_axes(pos_f)')
s=s.replace('ax.set_xlabel("Share of impacts for which the station has the highest signal-to-noise ratio")','ax.set_xlabel("Share of impacts for which the station has the highest signal-to-noise ratio (η = 0.001)")')
s=s.replace('ax.set_title("f  Station with the highest predicted signal (panel rows a–d)", fontsize=8)','ax.set_title("f  Station with the highest predicted signal, same four uses of the 00:19 data", fontsize=8)')
s=s.replace('ax.legend(h_, l_, fontsize=6, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3)','ax.legend(h_, l_, fontsize=6, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.13), ncol=5)')
s=s.replace('''              ["η 0.001, corrected IMOS loss", "η 0.00021 (F-35A), corrected", "open marker: before the correction"], fontsize=6, frameon=False, loc="lower right")''','''              ["coupling 0.001, corrected IMOS loss", "coupling 0.00021 (F-35A), corrected", "open marker: before the correction"], fontsize=6, frameon=False, loc="lower right")''')
s=s.replace('''        ax.text(0.03, 0.97, f"detectable at the best station\\nη 0.001''','''        ax.text(0.03, 0.97, f"detectable at the best station\\nη 0.001''')
open('charts_levels.py','w').write(s)
E
grep -n "hgt" charts_levels.py | head