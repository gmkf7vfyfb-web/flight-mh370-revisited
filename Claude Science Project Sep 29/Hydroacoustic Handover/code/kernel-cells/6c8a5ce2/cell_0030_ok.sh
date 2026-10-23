cd .tmp/standin; python - <<'EOF'
s=open("run_event_tl.py").read()
s=s.replace('''CE.SP.convert = copy_convert''','''CE.SP.convert = copy_convert


def path_tl(exp, name, rd, out):
    """Copy of CE.path_tl with ONE change (disclosed): the receiver-range index [..., -1] is added to
    s["p"][0, js, 0], which is a length-1 array; float() of it raises TypeError under this numpy. Same
    indexing as f35a_eta_calibration.f35a_tl (tlz[-1]) and the audit's sus_tl.py. No other change."""
    stub = out / "stubschema"; stub.mkdir(parents=True, exist_ok=True)
    CE.SP.convert(Path(exp), stub, name)
    tag_ = name.replace("-", "_")
    bathy = pd.read_csv(stub / f"bathy_{tag_}.csv"); ssp = pd.read_csv(stub / f"ssp_{tag_}.csv")
    rprof, profiles = CE.A.build_profiles(bathy, ssp)
    rows = []
    for fc in CE.F.BANDS:
        tag = f"f{fc:g}".replace(".", "p")
        r, tl, nm, dt = CE.K.tl_path(out / "work" / name, tag, fc, profiles, rprof, np.array([rprof[-1]]), CE.F.SRC, [rd],
                                     CE.A.BOTTOMS["hard"], CE.AT_BIN, fg=CE.A.FG)
        s = CE.K.read_shd(out / "work" / name / f"{tag}.shd"); x = s["rr_m"] / 1000.0 / 6371.0
        sph = 10 * np.log10(x / np.sin(x))
        for js, zs in enumerate(s["sz"]):
            rows.append(dict(path=name, fc_hz=fc, src_depth_m=float(zs), rcv_depth_m=rd, range_km=float(rprof[-1]),
                             tl_db=float(-20 * np.log10(np.abs(s["p"][0, js, 0, -1])) + sph[-1]),
                             n_modes_first=nm[0] if nm else -1, n_modes_min=min(nm) if nm else -1))
    return pd.DataFrame(rows), np.nan''')
s=s.replace("d, _ = CE.path_tl(paths, name, rd, out)","d, _ = path_tl(paths, name, rd, out)")
open("run_event_tl.py","w").write(s)
EOF
export OMP_NUM_THREADS=1; P="$(cd ..; pwd)/hy/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"; rm -rf smoke40; ( time python run_event_tl.py "$P" "$(cd ../at; pwd)" /Users/pete/Downloads/mh370-exchange/ocean-transport/paths-calibration smoke40 40 ) 2>&1 | tail -5; cat smoke40/event_tl.csv; du -sh smoke40