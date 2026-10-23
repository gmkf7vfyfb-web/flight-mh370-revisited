cd trace && python - <<'EOF'
from PIL import Image, ImageDraw
a=Image.open('../src/pmc24/41598_2024_60529_Fig8_HTML.jpg').convert('RGB')
c=a.crop((0,660,749,791)).resize((749*2,131*2)); d=ImageDraw.Draw(c)
for x in range(0,749,25): d.line([(2*x,0),(2*x,8)],fill=(255,0,0)); d.text((2*x+1,8),str(x),fill=(255,0,0))
for y in range(660,791,10): d.line([(0,2*(y-660)),(10,2*(y-660))],fill=(0,160,0)); d.text((12,2*(y-660)-5),str(y),fill=(0,160,0))
c.save('crop_f8_h10n.png')
EOF