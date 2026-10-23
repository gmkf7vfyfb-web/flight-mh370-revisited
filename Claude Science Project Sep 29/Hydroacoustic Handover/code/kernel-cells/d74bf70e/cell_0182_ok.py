p="repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/build_path_stub.py"
t=open(p).read()
reps=[
('Approved 2026-10-09 (coordination/HYDROACOUSTICS.md, morning rulings, item 5): WOA23 + GEBCO on the\nair9 -> H01W and air9 -> H08S paths,',
 'Approved 2026-10-09 (coordination/HYDROACOUSTICS.md, morning rulings, item 5; extended to air8 by ruling\nH3): WOA23 + GEBCO on the air9 and air8 -> H01W and -> H08S paths,'),
('SOURCE: the air9 line midpoint from data/blackman/blackman_shot_lines.csv (both segments, 19 Oct 2001,\n02:10-02:46 UTC): -27.5612, 98.8821.',
 'SOURCES: line midpoints from data/blackman/blackman_shot_lines.csv (both segments of each line):\nair9 (19 Oct 2001, 02:10-02:46 UTC) -27.5612, 98.8821; air8 (16 Oct 2001, 12:28-13:04 UTC) -23.4246, 88.2167.'),
('SRC = ("air9", -27.5612, 98.8821)', 'SOURCES = {"air9": (-27.5612, 98.8821), "air8": (-23.4246, 88.2167)}'),
('Run: python prepare/build_path_stub.py <out_dir>', 'Run: python prepare/build_path_stub.py <out_dir> [air9|air8]   (default air9)'),
('def main(out_dir):', 'def main(out_dir, source="air9"):\n    SRC = (source,) + SOURCES[source]'),
('f"bathy_air9_{name}.csv"', 'f"bathy_{source}_{name}.csv"'),
('f"ssp_air9_{name}.csv"', 'f"ssp_{source}_{name}.csv"'),
('out / "woa23_95A4_season16_box.nc"', 'out / f"woa23_95A4_season16_box_{source}.nc"'),
('out / "stub-manifest.json"', 'out / f"stub-manifest_{source}.json"'),
('    main(sys.argv[1])', '    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "air9")'),
]
for a,b in reps:
    assert t.count(a)==1, a[:60]; t=t.replace(a,b)
open(p,"w").write(t)
print("box check:", "lat=slice(-37, -4), lon=slice(68, 117)" in t)