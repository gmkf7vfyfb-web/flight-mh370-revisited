cd src; python -c "
import pymupdf; d=pymupdf.open('App2.6B_MarineBio2.pdf')
for i in [0,4,5,40,44,46,47,48,49]: d[i].get_pixmap(dpi=100).save(f'b26_p{i+1}.png')
"; ls b26*