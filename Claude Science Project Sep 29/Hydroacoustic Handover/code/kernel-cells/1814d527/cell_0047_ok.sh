cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/kadri_package/v2-2026-10-22" && python - <<'EOF'
import hashlib, pathlib, time
prov = {
 "predictions.csv": "build_predictions_v2.py on run J (74 seeds) + supplement, TL grid run-j-tl-grid/tables (block 2), noise proxies (results-data), 22 Oct 2026",
 "predictions_meta.json": "build_predictions_v2.py: seeds, SHA-256 prefixes of inputs, mass shares, pooled medians",
 "windows.csv": "build_windows_v2.py from run-j-windows/request_windows.csv + windows.csv (block 3, bc99b07); reference rows from the brief, Kadri 2024, Royer 2016 Table 5, searches note",
 "reference_measure.py": "module draft of 9 Oct 2026 + M1b envelope matched filter (weak_signal/methods.py, 78c7e88), rewritten self-contained",
 "templates_envelope.npz": "make_templates.py from run-j-weak-signal/templates/templates_raw.npz (KRAKEN flat-profile synthesis, weak-signal track)",
 "templates_envelope.csv": "same, text form",
 "templates_meta.json": "make_templates.py summary",
 "pulse_runj.npz": "make_templates.py: 2,200 km template, tau = run J pooled median tau90 (predictions_meta.json), 5-40 Hz, 250 Hz",
 "synth_triad.py": "module draft of 9 Oct 2026, pulse replaced by pulse_runj.npz, coloured noise, 180 s",
 "selftest.py": "self-test driver (this package)",
 "selftest_results.csv": "selftest.py output, 36 runs x 5 bands",
 "selftest_summary.json": "selftest.py summary incl. M1b null threshold (60 noise-only runs)",
 "REQUESTS.md": "ask list (brief section 9, Refresh v2 sections 4-6, work order block 12; searches/windows/digitisation/TL-recalibration notes of 22 Oct)",
 "CALIBRATION_STATUS.txt": "rewritten from the 22 Oct results notes",
 "COVER_NOTE_FOR_PETE.md": "approval items and removal suggestions (internal; not for the recipient)",
 "README.md": "package contents and how to run on IMS triad data",
 "build_predictions_v2.py": "builder (module code)", "build_windows_v2.py": "builder (module code)", "make_templates.py": "builder (module code)",
 "stations.csv": "copy of module data/stations.csv (IMS triad elements, EarthScope FDSN, retrieved 2026-10-07) for synth_triad.py",
}
import shutil; shutil.copy("../../../data/stations.csv", "stations.csv")
lines = [f"# Kadri package v2 manifest, written {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}. sha256  size  file  provenance"]
for p in sorted(pathlib.Path('.').iterdir()):
    if p.name in ("MANIFEST.txt",) or p.is_dir(): continue
    h = hashlib.sha256(p.read_bytes()).hexdigest(); lines.append(f"{h}  {p.stat().st_size:>9d}  {p.name}  --  {prov.get(p.name, 'UNLISTED')}")
syn = pathlib.Path('/Users/pete/Downloads/mh370-exchange/hydroacoustics/kadri-package-v2/synthetic_triad')
for p in sorted(syn.iterdir()):
    h = hashlib.sha256(p.read_bytes()).hexdigest(); lines.append(f"{h}  {p.stat().st_size:>9d}  synthetic_triad/{p.name}  --  selftest.py via synth_triad.py (exchange copy only; not in git)")
pathlib.Path("MANIFEST.txt").write_text("\n".join(lines) + "\n")
print("\n".join(l.split('  --')[0] for l in lines[:25]))
EOF
# exchange copy + zip
EXD=/Users/pete/Downloads/mh370-exchange/hydroacoustics/kadri-package-v2
rsync -a --exclude synthetic_triad ./ $EXD/
cd $EXD/.. && rm -f kadri-package-v2/kadri-package-v2.zip && zip -qr kadri-package-v2/kadri-package-v2-2026-10-22.zip kadri-package-v2 -x 'kadri-package-v2/*.zip' && ls -la kadri-package-v2/ && du -sh kadri-package-v2
cd kadri-package-v2 && shasum -a 256 *.csv *.md *.txt *.json *.npz *.py *.zip > SHA256SUMS && wc -l SHA256SUMS
grep -il "fund" $EXD/* 2>/dev/null | head