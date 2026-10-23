mkdir -p royer_pages; cp rr/royer2016.pdf royer-2016-LDO-201608.pdf; python - <<'EOF'
import pymupdf
d=pymupdf.open('rr/royer2016.pdf')
for i,p in enumerate(d):
    p.get_pixmap(dpi=150).save(f'royer_pages/royer2016_p{i+1:02d}.png')
    print(i+1, len(p.get_images()), round(p.rect.width), round(p.rect.height))
EOF