cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"; python - <<'EOF'
s=open('tl_recal_block9.py').read()
old='''OUTPUTS. results-data/tl_recal_block9/:'''
new='''AMENDMENT 2 (22 Oct 2026 02:45 UTC, after the +/-20 km result was seen; EXPLORATORY, labelled, outside the
  pre-registered rule). The least-loss TL falls steadily with offset to the right of the geodesic (crest 1,199 m at
  0 km, 1,420 m at +20 km), and a bathymetry scan shows the feature cleared at +40 to +50 km (crest >= 1,572 m, the
  H01W slope itself). Offsets +30, +40, +50 km are added as an extension of the 3-D proxy. They are reported as an
  exploratory upper bound only; the step (d) verdict is taken from the registered +/-20 km set. The RAM (d3) runs are
  placed on the geodesic and on the +20 km path at 31.5 and 40 Hz.
OUTPUTS. results-data/tl_recal_block9/:'''
assert old in s; s=s.replace(old,new,1)
old2='''if __name__ == "__main__":'''
new2='''def cmd_tl_ext(sections, at, scratch, out, nproc=3):
    """Amendment 2: +30, +40, +50 km offset paths for air7 -> H01W (exploratory extension)."""
    sec = Path(sections); out = Path(out); pos, _ = site_pos_heading("air7"); rd = STATIONS["H01W"][1]
    jobs = []
    for d in (30.0, 40.0, 50.0):
        b, R = offset_section(pos, STATIONS["H01W"][0], d); b.to_csv(sec / "builder" / f"bathy_air7off{d:+.0f}_H01W.csv", index=False)
        for fc in AIR7_BANDS:
            jobs.append((f"air7off{d:+.0f}_H01W", sec / "builder" / f"bathy_air7off{d:+.0f}_H01W.csv", sec / "builder" / "ssp_air7_H01W.csv", fc, [10.0], rd, scratch, at))
    rows = []
    with Pool(int(nproc)) as P:
        for r in P.imap_unordered(tl_job, jobs):
            rows += r
    E = pd.DataFrame(rows); E["extension"] = True; E.to_csv(out / "tl_runs_ext.csv", index=False)
    print(E.pivot(index="fc_hz", columns="tag", values="tl_db").round(1).to_string())


def ram_job(a):
    """RAM (pyram) band TL at the path end, ram_tl_check settings (dr 2 lambda, dz lambda/20, 9 frequencies, no absorption)."""
    tag, bathy_csv, ssp_csv, fc, zs, rd = a
    from pyram.PyRAM import PyRAM
    b = pd.read_csv(bathy_csv); s = pd.read_csv(ssp_csv)
    rprof, prof = A.build_profiles(b, s); nodes = A.node_profiles(s); keys = sorted(nodes)
    nr = np.array([nodes[k][0] for k in keys]); z = nodes[keys[0]][1]; Cm = np.vstack([nodes[k][2] for k in keys]).T
    D = np.array([p[0] for p in prof])
    if D.max() >= z[-1]:
        z = np.append(z, D.max() + 100.0); Cm = np.vstack([Cm, Cm[-1:]])
    L = rprof[-1] * 1e3; t0 = time.time(); I = []
    for f in fc * 2 ** (np.linspace(-1, 1, 9) / 6):
        lam = 1500.0 / f
        m = PyRAM(f, zs, rd, z, nr * 1e3, Cm, np.array([0.0]), np.array([0.0]), np.array([[A.BOTTOMS["hard"]["cp"]]]), np.array([[A.BOTTOMS["hard"]["rho"]]]),
                  np.array([[A.BOTTOMS["hard"]["ap"]]]), np.column_stack([rprof * 1e3, D]), rmax=L, zmplt=D.max(), dr=2 * lam, dz=lam / 20, ndr=1, ndz=1)
        r = m.run(); rr, tl = r["Ranges"], r["TL Line"]; k = rr >= rr[-1] - 500.0
        I.append(np.mean(10 ** (-tl[k] / 10)))
    x = L / 1000.0 / 6371.0
    return dict(tag=tag, fc_hz=fc, src_depth_m=zs, tl_ram_db=float(-10 * np.log10(np.mean(I)) + 10 * np.log10(x / np.sin(x))), wall_s=time.time() - t0)


def cmd_ram(sections, at, scratch, out, nproc=4):
    sec = Path(sections); out = Path(out); rd = STATIONS["H01W"][1]
    paths = {"air7off+0_H01W": sec / "builder" / "bathy_air7off+0_H01W.csv", "air7off+20_H01W": sec / "builder" / "bathy_air7off+20_H01W.csv"}
    jobs = [(tag, p, sec / "builder" / "ssp_air7_H01W.csv", fc, 10.0, rd) for tag, p in paths.items() for fc in (31.5, 40.0)]
    jobs.append(("builder_air9_H01W", sec / "builder" / "bathy_air9_H01W.csv", sec / "builder" / "ssp_air9_H01W.csv", 31.5, 10.0, rd))
    jobs.append(("builder_air9_H01W", sec / "builder" / "bathy_air9_H01W.csv", sec / "builder" / "ssp_air9_H01W.csv", 40.0, 10.0, rd))
    # matched KRAKEN without absorption (same convention as ram_tl_check: no Francois-Garrison in either model)
    krows = []
    for tag, p, sspc, fc, zs, rdd in jobs:
        bth = pd.read_csv(p); ssp = pd.read_csv(sspc); rprof, profiles = A.build_profiles(bth, ssp); L = float(rprof[-1]); root = f"noabs_{tag}_f{fc:g}".replace(".", "p")
        try:
            K.tl_path(scratch, root, fc, profiles, rprof, np.array([L]), [zs], [rdd], A.BOTTOMS["hard"], at, fg=None)
            sh = K.read_shd(Path(scratch) / f"{root}.shd"); x = L / 6371.0
            krows.append(dict(tag=tag, fc_hz=fc, tl_kraken_noabs_db=float(-20 * np.log10(np.abs(sh["p"][0, 0, 0, -1])) + 10 * np.log10(x / np.sin(x)))))
        except RuntimeError:
            krows.append(dict(tag=tag, fc_hz=fc, tl_kraken_noabs_db=np.inf))
    with Pool(int(nproc)) as P:
        R = pd.DataFrame(list(P.imap_unordered(ram_job, jobs)))
    R = R.merge(pd.DataFrame(krows), on=["tag", "fc_hz"]); R.to_csv(out / "air7_ram.csv", index=False); print(R.round(1).to_string(index=False))


if __name__ == "__main__":'''
assert old2 in s; s=s.replace(old2,new2,1)
s=s.replace('''    elif cmd == "air7":
        cmd_air7(*sys.argv[2:5])''','''    elif cmd == "air7":
        cmd_air7(*sys.argv[2:5])
    elif cmd == "tl_ext":
        cmd_tl_ext(*sys.argv[2:6], *(sys.argv[6:7] or ["3"]))
    elif cmd == "ram":
        cmd_ram(*sys.argv[2:6], *(sys.argv[6:7] or ["4"]))''')
open('tl_recal_block9.py','w').write(s)
import ast; ast.parse(s); print('ok')
EOF
AT=$OLDPWD/tools; W=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tlrecal
export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
time python tl_recal_block9.py tl_ext $W/sections $AT $W/scratch ../results-data/tl_recal_block9 3