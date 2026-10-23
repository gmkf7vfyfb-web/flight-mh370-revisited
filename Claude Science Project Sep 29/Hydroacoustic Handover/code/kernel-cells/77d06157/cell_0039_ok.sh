cd gfx && python - <<'E'
s=open('charts_levels.py').read()
s=s.replace('ax.plot([i - 0.45, i + 0.45], [r.p50, r.p50], color="#252525", lw=1.6, zorder=2)','ax.plot([i - 0.45, i + 0.45], [r.p50, r.p50], color="#252525", lw=1.3, zorder=6)')
s=s.replace('ax.plot([x25 - 0.45, x25 + 0.45], [r.p50, r.p50], color="#252525", lw=1.6, zorder=2)','ax.plot([x25 - 0.45, x25 + 0.45], [r.p50, r.p50], color="#252525", lw=1.3, zorder=6)')
s=s.replace('lines = ["η          matched filter   baseline"] if not compact else ["η: matched filter / baseline"]','lines = ["coupling   matched filter   baseline"] if not compact else ["coupling: matched filter / baseline"]')
s=s.replace('lines.append(f"with 2014 noise (−6.0 dB): {pct(r1.frac_matched_filter_kadri_noise)} at 0.001, {pct(r2.frac_matched_filter_kadri_noise)} at 0.00021")',
 'lines.append(f"matched filter, 2014 noise 6 dB quieter:"); lines.append(f"{pct(r1.frac_matched_filter_kadri_noise)} at 0.001, {pct(r2.frac_matched_filter_kadri_noise)} at 0.00021")')
s=s.replace('ax = fig.add_axes([0.085, b + 0.075, 0.895, 0.86 - b - 0.075 - 0.075])','ax = fig.add_axes([0.085, b + 0.075, 0.895, 0.865 - b - 0.075])')
s=s.replace('h.append(Line2D([], [], color="#252525", lw=1.6)','h.append(Line2D([], [], color="#252525", lw=1.3)') 
s=s.replace('h = [Line2D([], [], color="#252525", lw=1.6), Patch','h = [Line2D([], [], color="#252525", lw=1.3), Patch')
open('charts_levels.py','w').write(s)
E