A="audit/repo/Claude Science Project Sep 29/results/hydroacoustics-audit"; cd "$A/scripts"; python3 - <<'EOF'
s=open('charts.py').read()
s=s.replace('label=f"Background noise, May–June 2003: median of {len(v)} records")','label=f"Background noise, May–June 2003: median ({len(v)} records)")')
s=s.replace('textwrap.fill(tech, 245)','textwrap.fill(tech, 232)').replace('textwrap.fill(ste, 205)','textwrap.fill(ste, 200)')
s=s.replace('fig.text(0.01, 0.24,','fig.text(0.01, 0.232,')
s=s.replace('bbox_to_anchor=(0.685, 0.90)','bbox_to_anchor=(0.682, 0.90)')
open('charts.py','w').write(s)
EOF
cd - >/dev/null; M="audit/hb/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"; python "$A/scripts/charts.py" "$M" "$A/data/markers_audit.json" "$A" 2>&1 | tail -3; python3 -c "
from PIL import Image; im=Image.open('$A/hydroacoustics-audit-noise-vs-impact-H01W.png'); print(im.size); im.crop((1500,150,2700,700)).save('audit/work/crop_leg.png'); im.crop((0,1700,2700,1980)).save('audit/work/crop_foot.png')"