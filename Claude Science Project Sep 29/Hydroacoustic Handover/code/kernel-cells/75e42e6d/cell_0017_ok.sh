cd src; python -c "
import pymupdf; d=pymupdf.open('SIR_2018_official.pdf'); p=d[73]; p.get_pixmap(dpi=200).save('sir_p74.png'); print(p.get_text()[:300])"