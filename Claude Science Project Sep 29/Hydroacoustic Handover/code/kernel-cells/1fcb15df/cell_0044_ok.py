
from matplotlib.patches import Rectangle, Patch
VC = {"not held":("#e6e6e6","No recording held"),"could_not":("#c6dbef","Held: candidate too weak to see there; nothing"),
      "should":("#9e9ac8","Held: should have seen (detection probability >= 0.5); nothing"),
      "present":("#fdae6b","Held: candidate or another row at p <= 0.05 present"),
      "nm_nothing":("#f7f7f7","Held: no level model; nothing / no Royer arrival"),"pick":("#99d8c9","Held (Royer only): Royer marks an arrival in the window")}
colshort = {("H01W","kadri"):"Cape Leeuwin\n(Kadri, digitised)",("H01W","royer"):"Cape Leeuwin\n(Royer, digitised)",("H08S","kadri"):"Diego Garcia S.\n(Kadri, digitised)",
  ("H08N","none"):"Diego Garcia N.",("3315","imos"):"Perth Canyon\n3315",("3376","imos"):"Perth Canyon\n3376",("3274","imos"):"Portland\n3274",("3275","imos"):"Portland\n3275",
  ("3250","imos"):"Scott Reef\n3250",("NEAMS","none"):"NEAMS",("SWAMS","royer"):"SWAMS\n(Royer)",("SSEIR","royer"):"SSEIR\n(Royer)",("MAD","royer"):"MAD\n(Royer)",
  ("WKER","royer"):"WKER\n(Royer)",("NCRO","royer"):"NCRO\n(Royer)"}
apply_figure_style(sizes=(8,7,6))
nC, nR = len(cands), len(ROWS)
fig = plt.figure(figsize=(17, 11.2)); ax = fig.add_axes([0.17, 0.25, 0.82, 0.62])
for i, c in enumerate(cands):
    for j, (rx, kind) in enumerate(ROWS):
        r = MX[(MX.candidate==c["name"])&(MX.receiver==rx)&(MX.data_source==kind)].iloc[0]
        col = VC[r.verdict_class][0]; ax.add_patch(Rectangle((j, i), 1, 1, fc=col, ec="white", lw=1.5))
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
ax.tick_params(length=0)
ax.axhline(5, color="#333333", lw=1.0)
fig.text(0.01, 0.975, "Of 150 candidate-receiver cells, 65 hold no recording; where recordings are held and the candidate should have been seen, nothing is there",
         fontsize=9.5, ha="left", va="top")
fig.text(0.01, 0.95, "Rows: the five strongest two-site pairs and the five strongest single-site signals. Columns: every receiver. Cell: data held in the predicted arrival window, "
         "the largest matched-filter p (or Royer spectrogram peak) in it, and the expected level of the candidate (dB above the background median) at the coupling it needs.",
         fontsize=7, ha="left", va="top")
handles = [Patch(fc=v[0], ec="#999999", lw=0.5, label=v[1]) for v in VC.values()]
fig.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.17, 0.165), ncol=3, frameon=False, fontsize=7)
f1 = ("(i) Each row is one candidate sound. Each column is one receiver. A grey cell means that we hold no recording for the time when the sound would arrive. A purple cell means "
      "that we hold a recording, the model says the receiver should have detected the candidate, and the recording shows nothing. The strongest pair (row 1) has two such cells: Perth "
      "Canyon 3376 and Portland 3274. The Cape Leeuwin signal of that pair is at the time of an arrival that Royer marks for his event A, an ice-quake far to the south. Digitised means "
      "copied from a published figure. These are model predictions; the sound-loss model and the coupling are not calibrated.")
f2 = ("(ii) Source posterior = run J (search-geometry sample: waypoints stratum seeds 1-8 + northern supplement, 00:19 Held Out, p 0.5). Pairs: arc lag locus (offset 0), MC n 4,000, "
      "c ~ N(1.482, 0.006) km/s, pick sd 3.6 s; singles: sample conditioned on the arrival. Window = 2.5-97.5 % predicted arrival. p = M1b window-maximum p vs own-logger 1-15 Mar null "
      "(3315<-3376, 3275<-3274; panels: 3376 via plot emulator), not trials-corrected (CSV gives the corrected value). Expected level = peak 1 s 5-40 Hz SNR at the coupling eta for P_D = 0.5 "
      "at the defining receiver(s) (jointly for pairs), or eta 0.01 where eta is undefined; IMOS TL = RAM-corrected arc table; IMS = proxy noise, +4.8 dB triad gain; P_D = block 7 logistic, "
      "alpha 0.05. Strongest pair: locus 33.6 S 94.5 E, impact 00:31:41, eta 0.069 = 330x F-35A 2.1e-4 (composition v2); bearing from H01W 268.9 deg vs Kadri 57 / 306.18 deg (none within 37 deg; "
      "nearest Table 1 bearing 00:52:50 at 274.84 deg, 46 s later). Royer event A pick bar at H01W-2 on his Fig. 4: 00:51:56.8-00:52:04.5 (Table 5: 00:51:41-43; table-figure offset 13.6-16 s "
      "unresolved). Kadri times: text time 00:52:03, caption time 00:54:30. Single 5 needs an impact before 00:19:29 (no run J support). Scott Reef 3250 and Portland from north of ~29 S: path blocked in "
      "the TL grid. PREDICTIVE, NOT CALIBRATED; C1 (slope misfit +10.4/+7.4 dB/oct at H01W/H08S), C2 (coupling not calibrated).")
fig.text(0.01, 0.13, "\n".join(textwrap.wrap(f1, 250)), fontsize=6.8, ha="left", va="top")
fig.text(0.01, 0.075, "\n".join(textwrap.wrap(f2, 300)), fontsize=6.0, ha="left", va="top", color="#333333")
fig.savefig(f"{OUT}/arrival_window_matrix.png", dpi=200); fig.savefig(f"{OUT}/arrival_window_matrix.pdf"); plt.close(fig)
