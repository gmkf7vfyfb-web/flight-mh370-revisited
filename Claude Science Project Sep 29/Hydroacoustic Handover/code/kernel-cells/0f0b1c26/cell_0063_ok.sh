cd trace && python - <<'EOF'
from PIL import Image, ImageDraw
a=Image.open('../src/pmc24/41598_2024_60529_Fig8_HTML.jpg').convert('RGB')
for nm,(t,b) in {'p1':(120,250),'p2':(385,520)}.items():
    c=a.crop((0,t,749,b)).resize((749*2,(b-t)*2)); d=ImageDraw.Draw(c)
    for y in range(t,b,10): d.line([(0,2*(y-t)),(10,2*(y-t))],fill=(0,160,0)); d.text((12,2*(y-t)-5),str(y),fill=(0,160,0))
    c.save(f'crop_f8_{nm}.png')
EOF