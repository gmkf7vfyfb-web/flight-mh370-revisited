cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"; python - <<'EOF'
s=open('tl_recal_block9_charts.py').read()
# panel a
s=s.replace('''        x = np.log2(n.fc_hz); c = np.polyfit(x, n.r_db - n.r_db.median(), 1); ax.plot(n.fc_hz, np.polyval(c, x), "-", color=cols[st], lw=0.8, alpha=0.6)
        ax.text(n.fc_hz.iloc[-1] * 1.05, np.polyval(c, x.iloc[-1]), f"{g.slope:+.1f} ± {g.slope_se:.1f} dB/oct", fontsize=7, color=cols[st], va="center")
    ax.set_title("a  Measured − predicted, level removed:\\n   the tilt is gone once the source spectrum is used", fontsize=9, loc="left")''',
'''        x = np.log2(n.fc_hz); c = np.polyfit(x, n.r_db - n.r_db.median(), 1); ax.plot(n.fc_hz, np.polyval(c, x), "-", color=cols[st], lw=0.8, alpha=0.6)
        ax.text(0.03, 0.04 + 0.06 * (st == "H08S"), f"{st} slope now {g.slope:+.1f} ± {g.slope_se:.1f} dB/oct", fontsize=7, color=cols[st], transform=ax.transAxes)
    ax.set_title("a  Measured − predicted, level removed:\\n   the tilt falls to within 3 dB per octave", fontsize=9, loc="left")''')
s=s.replace('''    ax.legend(fontsize=7, frameon=False, loc="upper left")
    ax = axes[1]''','''    ax.legend(fontsize=7, frameon=False, loc="upper right")
    ax = axes[1]''')
# panel b
s=s.replace('''        g = CGn[(CGn.station == st)].iloc[0]
        ax.text(c.fc_hz.iloc[-1] * 1.05, c.r_tilde_db.iloc[-1], f"{g.slope:+.1f} ± {g.slope_se:.1f} dB/oct", fontsize=7, color=cols[st], va="center")
    ax.set_title("b  After removing the part common to both stations\\n   (the path-only view): within 2 dB", fontsize=9, loc="left"); ax.legend(fontsize=7, frameon=False)''',
'''        g = CGn[(CGn.station == st)].iloc[0]
        ax.text(0.03, 0.04 + 0.06 * (st == "H08S"), f"{st} slope {g.slope:+.1f} ± {g.slope_se:.1f} dB/oct", fontsize=7, color=cols[st], transform=ax.transAxes)
    ax.set_title("b  After removing the part common to both stations\\n   (the path-only view): within 3 dB", fontsize=9, loc="left"); ax.legend(fontsize=7, frameon=False, loc="upper right")''')
# panel c
s=s.replace('''    ax.text(c.fc_hz.iloc[-1] * 1.05, cm.iloc[-1], f"{g.slope:+.1f} ± {g.slope_se:.1f} dB/oct", fontsize=7, color=GREEN, va="center")''',
'''    ax.text(0.03, 0.04, f"slope now {g.slope:+.1f} ± {g.slope_se:.1f} dB/oct", fontsize=7, color=GREEN, transform=ax.transAxes)''')
open('tl_recal_block9_charts.py','w').write(s)
EOF
RES="$PWD/../../../../../../repo/Claude Science Project Sep 29/results"
python tl_recal_block9_charts.py ../results-data/tl_recal_block9 "$RES" "$RES/hydroacoustics-audit/data/air9_residuals.csv" 2>&1 | tail -1