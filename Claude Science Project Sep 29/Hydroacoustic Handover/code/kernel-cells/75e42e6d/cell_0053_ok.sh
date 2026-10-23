cd src; grep -n "Figure 1.12A\|Appendix1.12A\|02 July 2018" sir.txt | head -3; grep -n -i "22.3\|Tableau 8\|A2-G1" App2.6B_MarineBio2.txt | head; python -c "
import pymupdf; d=pymupdf.open('App2.6B_MarineBio2.pdf')
for i in [41,42,43]: d[i].get_pixmap(dpi=90).save(f'b26_p{i+1}.png')"