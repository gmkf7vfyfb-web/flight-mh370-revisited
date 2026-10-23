python - <<'EOF'
import pathlib
p=pathlib.Path("note_fill.py"); s=p.read_text()
s=s.replace('''cov = pd.read_csv(TN / "imos_tl_ram_coverage.csv", dtype={"logger": str})''','''print("\\n## new - old TL by latitude band (open rows, 10 m, offset 0): median over 5-40 Hz bands >= 12.5 Hz | 5-10 Hz; south (41-33 S) | north (32.5-20 S)")
for lg in L:
    g = mo[mo.logger == lg]; out = []
    for nm, sel in (("41-33 S", g.lat_old <= -33), ("32.5-20 S", g.lat_old > -33)):
        for bn, bs in ((">=12.5 Hz", g.fc_hz >= 12.5), ("5-10 Hz", g.fc_hz <= 10)):
            h = g[sel & bs].dd; out.append(f"{nm} {bn}: {h.quantile(.1):+.0f}/{h.median():+.0f}/{h.quantile(.9):+.0f} (n={len(h)})")
    print(NM[lg], " | ".join(out))
cov = pd.read_csv(TN / "imos_tl_ram_coverage.csv", dtype={"logger": str})''')
p.write_text(s)
EOF
python note_fill.py /tmp/interim/tables 2>&1 | grep -A6 "latitude band"