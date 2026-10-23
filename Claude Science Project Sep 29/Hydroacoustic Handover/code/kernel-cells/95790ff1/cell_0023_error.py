pg=doc[22]
img=pg.render(scale=600/72).to_pil()
W,H=img.size
fig23=img.crop((int(W*0.12),int(H*0.605),int(W*0.42),int(H*0.9)))
fig23.save("crops/fig23_600dpi.png"); print(fig23.size)
# check whether embedded image resolution is low: list page objects
for o in pg.get_objects():
    if o.type==pdfium.raw.FPDF_PAGEOBJ_IMAGE:
        print('img', o.get_pos(), o.get_size() if hasattr(o,'get_size') else '')