cd "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/5e788282-a899-406d-be81-a794b69469f6/hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/metz_f35a"
python - <<'E'
s=open('charts.py').read()
rep=[
('''    ax.set_title(f"{'Wake Island north' if st == 'H11N' else 'Wake Island south'} ({st}), {S5['triads'][st]['profile']['L_km']:,.0f} km: measured width at half power {o['w3_s']:.1f} s", loc="left")''',
 '''    ax.set_title(f"{'Wake Island north' if st == 'H11N' else 'Wake Island south'} ({st}), {S5['triads'][st]['profile']['L_km']:,.0f} km\\nwidth 6 dB below the peak: measured {o['w6_s']:.1f} s, model {S5['triads'][st]['model_at_tau5']['model_w6_s']:.1f} s", loc="left")'''),
('''axes[0].set_ylabel("Sound energy above the background,\\nrelative to the peak (dB)"); axes[0].legend(frameon=False, loc="lower left")''',
 '''axes[0].set_ylabel("Sound energy above the background,\\nrelative to the peak (dB)"); axes[1].legend(frameon=False, loc="upper right", fontsize=6.5)'''),
('''fig.suptitle("The modelled sound channel gives an arrival as short as the measured F-35A arrival, whatever the source duration", x=0.01, ha="left", fontsize=9)
fig.subplots_adjust(left=0.1, right=0.98, top=0.86, bottom=0.36, wspace=0.06)''',
 '''fig.suptitle("The modelled sound channel gives an arrival as short as the measured F-35A arrival,\\nwhatever the source duration", x=0.01, ha="left", fontsize=9)
fig.subplots_adjust(left=0.1, right=0.98, top=0.80, bottom=0.36, wspace=0.06)'''),
('''ax.axhline(2.1e-4, color=ORANGE, lw=1.2, ls="--"); ax.text(0.052, 2.1e-4 * 1.12, "value used until now, 2.1 × 10⁻⁴ (explosive-charge law, Brown et al. 2026)", color=ORANGE, fontsize=7)''',
 '''ax.axhline(2.1e-4, color=ORANGE, lw=1.2, ls="--"); ax.text(10.5, 2.1e-4 * 0.78, "value used until now, 2.1 × 10⁻⁴ (explosive-charge law, Brown et al. 2026)", color=ORANGE, fontsize=7, ha="right", va="top")'''),
('''ax.text(0.052, S2["routeB_eta_4_64_geomean"] * 1.12,''','''ax.text(10.5, S2["routeB_eta_4_64_geomean"] * 0.8,'''),
('''"measured spectrum, 4-64 Hz only: " + sci(S2['routeB_eta_4_64_geomean']), color=DARK, fontsize=7)''','''"measured spectrum, 4-64 Hz only: " + sci(S2['routeB_eta_4_64_geomean']), color=DARK, fontsize=7, ha="right", va="top")'''),
('''ax.set_title("From the measured F-35A arrival, about 2 × 10⁻³ of the impact energy became sound: ten times the value used until now", loc="left", fontsize=8.5)
fig.subplots_adjust(left=0.14, right=0.98, top=0.9, bottom=0.36)''',
 '''ax.set_title("From the measured F-35A arrival, about 2 × 10⁻³ of the impact energy became sound:\\nten times the value used until now", loc="left", fontsize=8.5)
fig.subplots_adjust(left=0.14, right=0.98, top=0.88, bottom=0.36)'''),
('''    ax.set_title(f"{NM[rx]}: even odds at {l_c:.0f} dB (model) and {l_s:.0f}-{l_n:.0f} dB (F-35A)", loc="left")''',
 '''    ax.set_title(f"{NM[rx]}\\nmatched filter at even odds: {l_c:.0f} dB (model), {l_s:.0f}-{l_n:.0f} dB (F-35A)", loc="left")'''),
('''fig.suptitle("On the real F-35A arrival the matched filter needs 4-10 dB more signal than on the model signal, and gains only 1-3 dB over STA/LTA", x=0.01, ha="left", fontsize=9)
fig.subplots_adjust(left=0.08, right=0.98, top=0.86, bottom=0.36, wspace=0.06)''',
 '''fig.suptitle("On the real F-35A arrival the matched filter needs 4-10 dB more signal than on the model signal,\\nand gains only 0-3 dB over STA/LTA", x=0.01, ha="left", fontsize=9)
fig.subplots_adjust(left=0.08, right=0.98, top=0.79, bottom=0.36, wspace=0.06)'''),
('''ax.set_title("The source spectrum implied by the F-35A arrival falls by 6-7 dB per octave, inside the range of the impact source model", loc="left", fontsize=8.5)
fig.subplots_adjust(left=0.14, right=0.98, top=0.9, bottom=0.36)''',
 '''ax.set_title("The source spectrum implied by the F-35A arrival falls by 6-7 dB per octave,\\ninside the range of the impact source model", loc="left", fontsize=8.5)
fig.subplots_adjust(left=0.14, right=0.98, top=0.88, bottom=0.36)'''),
('''ax.legend(frameon=False, fontsize=6.8, loc="lower left"); ax.spines[["top", "right"]].set_visible(False)
ax.set_title(f"The F-35A site''','''ax.legend(frameon=False, fontsize=6.8, loc="center right"); ax.spines[["top", "right"]].set_visible(False)
ax.set_title(f"The F-35A site'''),
]
for a,b in rep:
    assert a in s, a[:60]; s=s.replace(a,b)
open('charts.py','w').write(s)
E