P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
cd "$P" && python - <<'EOF'
import pathlib
p=pathlib.Path("imos_ram_grid_charts.py"); s=p.read_text()
s=s.replace('ax.text(41, CLIP_DB + 1.5, "above the line: path blocked (values up to 630 dB drawn at the edge)", fontsize=5.8, color="0.4", va="bottom")',
            'ax.text(41, CLIP_DB - 2.5, "at the dotted line: path blocked (up to 630 dB)", fontsize=5.8, color="0.4", va="top")')
p.write_text(s)
EOF
python -m py_compile imos_ram_grid_charts.py && echo ok; date