cd src; python -c "
import pymupdf; d=pymupdf.open('ATSB_search_areas_30jul2015.pdf')
for i in [17,19]: d[i].get_pixmap(dpi=130).save(f'sa_p{i+1}.png')
"; ls sa_p*