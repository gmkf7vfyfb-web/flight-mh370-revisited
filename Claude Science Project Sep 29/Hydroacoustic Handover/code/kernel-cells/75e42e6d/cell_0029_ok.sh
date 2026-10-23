cd src; grep -n -i "barnacle\|Lepas\|isotope\|marine biolog" sir.txt | head -40; python -c "
import pymupdf; d=pymupdf.open('App2.6B_MarineBio2.pdf')
for i in [1,2,3]: d[i].get_pixmap(dpi=110).save(f'b26_p{i+1}.png')
print(len(d))"