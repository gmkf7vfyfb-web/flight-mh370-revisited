cd src 2>/dev/null && ls ATSB_search_areas_30jul2015.pdf ATSB_OpSearch_2017.txt sir.txt research 2>/dev/null; cd ..; ls research-beacons-tpl-simulator-barnacles.md; cd src && python -c "
import pymupdf; d=pymupdf.open('ATSB_search_areas_30jul2015.pdf')
for i,n in [(17,'fig12'),(19,'fig14')]:
    p=d[i]; p.get_pixmap(dpi=220).save(f'../atsb2014_{n}_page{i+1}.png')
print('ok')"; ls -la ../atsb2014_*