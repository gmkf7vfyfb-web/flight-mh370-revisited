cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
python - <<'EOF'
import pathlib; p=pathlib.Path('tl_grid_charts.py'); s=p.read_text()
old='''    fig.legend(h, l, loc="upper right", ncol=4, bbox_to_anchor=(0.99, 0.945), title="Frequency band (third octave); thick line = on the arc, thin lines = 30 NM either side")'''
new='''    side = ", ".join(f"{int(abs(o))}" for o in sorted({abs(o) for o in offs if o != 0}))
    fig.legend(h, l, loc="upper right", ncol=4, bbox_to_anchor=(0.99, 0.945), title=f"Frequency band (third octave); thick line = on the arc, thin lines = {side} NM either side")'''
assert old in s; s=s.replace(old,new)
s=s.replace('"sends no sound through. The thin lines are for sources 30 nautical miles (56 km) west and east of the arc. In the orange band the source sits over "',
            '"sends no sound through. The thin lines are for sources 30 (and, where drawn, 60) nautical miles west and east of the arc. In the orange band the source sits over "')
p.write_text(s)
EOF
grep paths /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/raw/passC.log | tail -1; date -u