set -e; cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"; python - <<'EOF'
s=open('tl_recal_block9.py').read()
old='''TIMESTAMP CORRECTION'''
new='''AMENDMENT 4 (22 Oct 2026, after the parent's message that the Digitisation track has traced all Fig. 23 curves at the
  source limit, results-data/digitised/blackman-2004/, commit 1cb138a; written BEFORE any band mean of those traces is
  computed here). (i) Route 2 (F-35A): fetch_article_fulltext('10.1007/s00024-022-03117-6') was tried once and returned
  no full text or figures (closed access); route 2 is recorded as gap G4 and the block proceeds on route 1 alone.
  (ii) Step (d) observation is re-scored on the new CL air7 and air9 traces: third-octave dB means inside f_b 2^(+/-1/6)
  over all columns (ambiguous=1 columns included, their share reported), bands with >= 3 columns; the same step (d)
  statistic and 10 dB rule applied to the adiabatic set (registered) and to the RAM set (exploratory); the earlier
  airgun_sites_confirm digitisation is reported beside it. (iii) air1 -> H08N check (descriptive, single pair; the
  confirmatory rule of airgun_sites_confirm needs >= 3 pairs and is not re-opened): TL from airsites_tl.csv (audit builder,
  z_s 10 m, 9/12 reported), EW0112 source S0 + AF toward H08N (air1 heading from table1_shot_lines.csv, shot-weighted),
  observation from the new DGN air1 trace, bands 10-80 Hz readable in Fig. 2 (40 Hz excluded); SLOPE and SHAPE under C1,
  LEVEL reported only (G23: units). Compared with the uncorrected residual slope. Outputs: air7_corridor_v2.csv,
  air7_verdict_v2.json, air1_h08n_check.csv/json.
TIMESTAMP CORRECTION'''
assert old in s; s=s.replace(old,new,1)
old2='''if __name__ == "__main__":'''
new2='''def band_means_trace(csv, bands, min_cols=3):
    t = pd.read_csv(csv, comment="#"); rows = []
    for fc in bands:
        m = (t.f_hz >= fc * 2 ** (-1 / 6)) & (t.f_hz < fc * 2 ** (1 / 6))
        if m.sum() >= min_cols:
            rows.append(dict(fc_hz=fc, tl_obs_db=float(t.tl_db[m].mean()), n_cols=int(m.sum()), frac_ambiguous=float(t.ambiguous[m].mean())))
    return pd.DataFrame(rows).set_index("fc_hz")


def cmd_air7_v2(out, dig_dir):
    """Amendment 4 (ii): step (d) re-scored on the Digitisation track's CL air7/air9 traces."""
    out = Path(out); dig = Path(dig_dir)
    C = pd.read_csv(out / "air7_corridor.csv").set_index("fc_hz")
    o7 = band_means_trace(dig / "fig23_CL_air7_DIGITISED.csv", AIR7_BANDS); o9 = band_means_trace(dig / "fig23_CL_air9_DIGITISED.csv", AIR7_BANDS)
    ram = pd.concat([pd.read_csv(out / f) for f in ("air7_ram.csv", "air7_ram_ext.csv") if (out / f).exists()])
    a9r = ram[ram.tag == "builder_air9_H01W"].set_index("fc_hz").tl_ram_db
    R = C[["tl_geo_db", "tl_nx2d_db", "tl_least_loss_db", "tl_air9_H01W_db", "dtl_obs_db"]].copy().rename(columns={"dtl_obs_db": "dtl_obs_v1_db"})
    R["tl_obs_air7_v2_db"] = o7.tl_obs_db.reindex(R.index); R["tl_obs_air9_v2_db"] = o9.tl_obs_db.reindex(R.index)
    R["n_cols_air7"] = o7.n_cols.reindex(R.index); R["frac_amb_air7"] = o7.frac_ambiguous.reindex(R.index); R["frac_amb_air9"] = o9.frac_ambiguous.reindex(R.index)
    R["dtl_obs_v2_db"] = R.tl_obs_air7_v2_db - R.tl_obs_air9_v2_db
    for c in ("tl_geo_db", "tl_nx2d_db", "tl_least_loss_db"):
        R["excess_v2_" + c] = (R[c] - R.tl_air9_H01W_db) - R.dtl_obs_v2_db
    for tag in ("air7off+0_H01W", "air7off+20_H01W", "air7off+50_H01W"):
        r = ram[ram.tag == tag].set_index("fc_hz").tl_ram_db
        R["excess_v2_ram_" + tag.split("_")[0]] = (r - a9r).reindex(R.index) - R.dtl_obs_v2_db
    R = R.reset_index(); R.to_csv(out / "air7_corridor_v2.csv", index=False)
    prim = R[R.fc_hz.isin([31.5, 40.0, 50.0, 63.0]) & R.dtl_obs_v2_db.notna()]
    med = {c.replace("excess_v2_", ""): float(prim[c].median()) for c in R.columns if c.startswith("excess_v2_")}
    if abs(med["tl_nx2d_db"]) <= 10:
        verdict = "REPRODUCED"
    elif abs(med["tl_least_loss_db"]) <= 10:
        verdict = "REPRODUCED AS AN UPPER BOUND"
    else:
        verdict = "NOT REPRODUCED"
    V = dict(verdict_v2=verdict, median_excess_v2_db=med, bands_used=[float(f) for f in prim.fc_hz], dtl_obs_v2_by_band=prim.set_index("fc_hz").dtl_obs_v2_db.round(2).to_dict(),
             dtl_obs_v1_by_band=prim.set_index("fc_hz").dtl_obs_v1_db.round(2).to_dict(), source="results-data/digitised/blackman-2004 (Digitisation track, 1cb138a)")
    json.dump(V, open(out / "air7_verdict_v2.json", "w"), indent=1, default=float); print(R.round(1).to_string(index=False)); print(json.dumps(V, indent=1, default=float))


def cmd_air1(out, dig_dir, confirm_dir, ew_dir):
    """Amendment 4 (iii): air1 -> H08N single-pair check of the EW0112 source model (descriptive)."""
    out = Path(out); dig = Path(dig_dir); ew = Path(ew_dir)
    T = pd.read_csv(Path(confirm_dir) / "airsites_tl.csv"); T = T[(T.site == "air1") & (T.station == "H08N")]
    tab = pd.read_csv(dig / "table1_shot_lines.csv"); a1 = tab[tab.site == "air1"]
    n = np.array([len(range(int(x.split("-")[0]), int(x.split("-")[1]) + 1)) for x in a1.shot_numbers])
    az = np.array([G.inv(r.start_lon_deg, r.start_lat_deg, r.end_lon_deg, r.end_lat_deg)[0] % 360 for _, r in a1.iterrows()])
    mid = np.array([((r.start_lat_deg + r.end_lat_deg) / 2, (r.start_lon_deg + r.end_lon_deg) / 2) for _, r in a1.iterrows()])
    heading = float((az * n).sum() / n.sum()); pos = (mid * n[:, None]).sum(0) / n.sum()
    H08N = (-6.3375, 71.0021)   # triad centroid, data/stations.csv
    phi = (G.inv(pos[1], pos[0], H08N[1], H08N[0])[0] % 360) - heading
    ball = pd.read_csv(ew / "ew0112_fig2_ball_spectra_bands_DIGITISED.csv"); R1m = float(json.load(open(ew / "ew0112_fig2_scaling.json"))["R1m_mean_m"])
    readable = ball.groupby("fc_hz").readable.all(); lvl = ball.pivot(index="fc_hz", columns="shot", values="level_db_re_1upa2_hz_at_receiver").mean(axis=1)
    xg, yg, vol = array_layout(ew / "ewing_20gun_layout_ofr95228.csv"); w = vol ** (1 / 3)
    obs = band_means_trace(dig / "fig23_DGN_air1_DIGITISED.csv", ALL_BANDS)
    fcs = np.array([f for f in obs.index if 10 <= f <= 80 and readable.get(f, False)])
    rows, grades = [], []
    for zs in ZS:
        tl = T[T.src_depth_m == zs].set_index("fc_hz").tl_db.reindex(fcs).values
        dref = np.array([dref_array(f, zs, 30, 15, R1m, xg, yg, w) for f in fcs]); af = np.array([array_factor(f, phi, xg, yg, w) for f in fcs])
        S0 = lvl.reindex(fcs).values + 20 * np.log10(R1m) - dref
        rl_pred = S0 + af - tl; rl_obs = 235.0 - obs.tl_obs_db.reindex(fcs).values
        r = rl_obs - rl_pred; r_unc = -(obs.tl_obs_db.reindex(fcs).values - tl)
        for f_, a_, b_, c_ in zip(fcs, rl_obs, rl_pred, r):
            rows.append(dict(zs=zs, fc_hz=f_, rl_obs_db=a_, rl_pred_db=b_, r_db=c_, frac_ambiguous=float(obs.frac_ambiguous[f_])))
        sc = ew_score(r, fcs); su = ols(fcs, r_unc)
        grades.append(dict(zs=zs, n=len(fcs), heading=heading, phi_deg=phi, **sc, slope_se=ols(fcs, r)[1], slope_uncorrected=su[0], slope_uncorrected_se=su[1]))
    pd.DataFrame(rows).to_csv(out / "air1_h08n_check.csv", index=False); Gd = pd.DataFrame(grades); Gd.to_csv(out / "air1_h08n_grades.csv", index=False)
    json.dump(dict(bands=[float(f) for f in fcs], grades=Gd.to_dict("records")), open(out / "air1_h08n_check.json", "w"), indent=1, default=float)
    print(Gd.round(2).to_string(index=False))


if __name__ == "__main__":'''
assert old2 in s; s=s.replace(old2,new2,1)
s=s.replace('''    elif cmd == "ram_ext":''','''    elif cmd == "air7_v2":
        cmd_air7_v2(*sys.argv[2:4])
    elif cmd == "air1":
        cmd_air1(*sys.argv[2:6])
    elif cmd == "ram_ext":''')
open('tl_recal_block9.py','w').write(s); import ast; ast.parse(s); print('ok')
EOF
grep -n "H08N" ../data/stations.csv | head -3
export GIT_CONFIG_GLOBAL=/dev/null; URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
cd "$OLDPWD/hydro"; B=hypothesis/hydroacoustics; git fetch -q origin $B 2>/dev/null || true
echo "INBOX:"; git show origin/$B:"Claude Science Project Sep 29/coordination/HYDROACOUSTICS.md" | grep -n "^## " | tail -1
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE; git read-tree origin/$B
git add --sparse "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/tl_recal_block9.py"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C=$(git -c user.name="Hydroacoustic Module (TL recal track)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "Hydroacoustics block 9: amendment 4 pre-registered (route 2 -> gap G4 after one closed-access fetch; air7 re-scored on the Digitisation track's Fig. 23 traces; air1 -> H08N single-pair check) before computation")
git push -q "$URL" $C:refs/heads/$B 2>/dev/null && echo "PREREG4 COMMIT $C"