cd src; python -c "
import pymupdf; d=pymupdf.open('metron_af447.pdf')
d[41].get_pixmap(dpi=150).save('../metron_appB_table4_p39.png'); print(d[42].get_text()[:300])"