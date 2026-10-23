import pypdfium2 as pdfium, collections
doc=pdfium.PdfDocument(P)
for i in range(len(doc)):
    page=doc[i]
    c=collections.Counter()
    imgs=[]
    for o in page.get_objects(max_depth=5):
        c[o.type]+=1
        if o.type==pdfium.raw.FPDF_PAGEOBJ_IMAGE:
            try:
                w,h=o.get_px_size(); imgs.append((w,h, [round(v) for v in o.get_pos()]))
            except Exception as e: imgs.append(str(e))
    print(i+1, page.get_size(), dict(c), imgs[:8])