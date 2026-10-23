cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/injection_recovery_run_j"
python - <<'EOF'
p='eta_map.py'; s=open(p).read()
old_doc=s[s.index('TL: block 2 grid pass A'):s.index('Rows: 1-in-8')]
new_doc='''TL: as pre-registered -- (i) IMOS loggers: the module's RAM-corrected table (ram_check/imos_tl_ramcorr.csv, five quantile
paths 38.46-31.64 S, source depth 10 m, per band, linear in impact latitude, CLAMPED beyond the span: rows north of 31.64 S
are 'TL extrapolated (clamped)' and their share is reported); (ii) H01W/H08S: block 2 grid pass A (on-arc sources 41-20 S,
source depth 10 m; PROVISIONAL until that track's note is published). A band with no modes / land carries no energy.
Rows north of 20 S are 'TL pending (grid)'.
'''
s=s.replace(old_doc,new_doc)
# replace delta construction with a direct RAM table, and tl_for_rows for IMOS
old=s[s.index('    # RAM - KRAKEN delta for IMOS'):s.index('    return lats, tab, delta')]
new='''    # IMOS: the module's RAM-corrected TL at the five quantile paths (per band), by quantile-path latitude
    rc = pd.read_csv(MODULE / "results-data" / "ram_check" / "imos_tl_ramcorr.csv", dtype={"quantile": str, "logger": str})
    rc = rc[np.isclose(rc.src_depth_m, R.TL_SRC_DEPTH_M)]
    delta = {}
    for lg in ("3376", "3274", "3315", "3275"):
        ql = np.array([QLAT[q] for q in sorted(QLAT)]); D = np.full((len(ql), len(R.BANDS_HZ)), np.nan)
        for i, q in enumerate(sorted(QLAT)):
            for j, fc in enumerate(R.BANDS_HZ):
                r = rc[(rc.logger == lg) & (rc["quantile"] == q) & np.isclose(rc.fc_hz, fc)]
                if len(r) and np.isfinite(r.tl_db).any():
                    D[i, j] = float(r.tl_db.median())
        delta[lg] = (ql, D)
'''
s=s.replace(old,new)
old2=s[s.index('def tl_for_rows'):s.index('def main')]
new2='''def tl_for_rows(lat, rx, lats, tab, delta):
    """TL per band for impact latitudes. IMOS: RAM-corrected quantile-path table, linear in latitude, clamped (NaN band = no
    energy). IMS: grid pass A, linear in latitude on the grid; NaN where the nearest grid node is blocked."""
    if rx in delta:
        ql, D = delta[rx]; la = np.clip(lat, ql.min(), ql.max()); out = np.empty((len(lat), D.shape[1]))
        for j in range(D.shape[1]):
            col = D[:, j]; ok = np.isfinite(col)
            out[:, j] = np.interp(la, ql[ok], col[ok]) if ok.sum() >= 2 else np.nan
        return out
    T = tab[rx]; out = np.empty((len(lat), T.shape[1]))
    la = np.clip(lat, lats.min(), lats.max())
    for j in range(T.shape[1]):
        col = T[:, j]; ok = np.isfinite(col)
        v = np.interp(la, lats[ok], col[ok]) if ok.sum() >= 2 else np.full(len(la), np.nan)
        near = np.abs(la[:, None] - lats[None, :]).argmin(1)
        out[:, j] = np.where(ok[near], v, np.nan)
    return out


'''
s=s.replace(old2,new2)
s=s.replace('"tl_source": "block 2 grid pass A (provisional) + RAM-KRAKEN delta for IMOS",',
            '"tl_source": "IMOS: module RAM-corrected quantile-path table (clamped beyond 38.46-31.64 S); H01W/H08S: block 2 grid pass A (provisional)", "share_tl_extrapolated_imos": float((lat > -31.63642).mean()),')
open(p,'w').write(s)
EOF
python -c "import ast;ast.parse(open('eta_map.py').read());print('ok')"
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-injection
OMP_NUM_THREADS=1 python eta_map.py $OUT/inputs $OUT/run $OUT/eta 2>&1 | grep -v Warning | tail -14