
apply_figure_style(sizes=(8,7,6))
nC, nR = len(cands), len(ROWS)
fig = plt.figure(figsize=(17, 11.2)); ax = fig.add_axes([0.17, 0.25, 0.82, 0.62])
for i, c in enumerate(cands):
    for j, (rx, kind) in enumerate(ROWS):
        r = MX[(MX.candidate==c["name"])&(MX.receiver==rx)&(MX.data_source==kind)].iloc[0]
        ax.add_patch(Rectangle((j, i), 1, 1, fc=VC[r.verdict_class][0], ec="white", lw=1.5))
        lines = []
        if r.held:
            if kind in ("imos","kadri"): lines.append(f"p {r.p_window:.2g}" if pd.notna(r.p_window) else "no sample")
            elif pd.notna(r.max_band_excess_db): lines.append(f"+{r.max_band_excess_db:.0f} dB peak")
            if r.held_fraction < 0.999: lines.append(f"{100*r.held_fraction:.0f} % held")
            if r.verdict_class=="pick": lines.append("Royer arrival")
        else: lines.append("not held")
        if pd.notna(r.expected_snr_db) and np.isfinite(r.expected_snr_db): lines.append(f"exp. {r.expected_snr_db:+.0f} dB")
        elif rx in ("3250",) or (rx in MODELLED and c.get("snr")): lines.append("path blocked")
        if rx in c["rx"]: lines.insert(0, "defining")
        ax.text(j+0.5, i+0.5, "\n".join(lines), ha="center", va="center", fontsize=6.3, fontweight="bold" if rx in c["rx"] else "normal")
ax.set_xlim(0, nR); ax.set_ylim(nC, 0)
ax.set_xticks(np.arange(nR)+0.5); ax.set_xticklabels([colshort[k] for k in ROWS], fontsize=6.5); ax.xaxis.tick_top()
ylab = []
for c in cands:
    eta = c.get("eta_need", np.nan)
    es = (f"coupling needed {eta:.2g}" if np.isfinite(eta) else ("coupling: no value works" if eta==np.inf else "coupling: not defined"))
    ylab.append(c["name"].replace(" (strongest)", ", strongest").replace("Diego Garcia South","Diego Garcia S.") + "\n" + es)
ax.set_yticks(np.arange(nC)+0.5); ax.set_yticklabels(ylab, fontsize=6.5)
for s in ax.spines.values(): s.set_visible(False)
ax.tick_params(length=0); ax.axhline(5, color="#333333", lw=1.0)
fig.text(0.01, 0.975, MAT_TITLE, fontsize=9.5, ha="left", va="top")
fig.text(0.01, 0.95, MAT_SUB, fontsize=7, ha="left", va="top")
handles = [Patch(fc=v[0], ec="#999999", lw=0.5, label=v[1]) for v in VC.values()]
fig.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.17, 0.165), ncol=3, frameon=False, fontsize=7)
fig.text(0.01, 0.13, "\n".join(textwrap.wrap(MAT_F1, 250)), fontsize=6.8, ha="left", va="top")
fig.text(0.01, 0.075, "\n".join(textwrap.wrap(MAT_F2, 300)), fontsize=6.0, ha="left", va="top", color="#333333")
fig.savefig(f"{OUT}/arrival_window_matrix.png", dpi=200); fig.savefig(f"{OUT}/arrival_window_matrix.pdf"); plt.close(fig)
