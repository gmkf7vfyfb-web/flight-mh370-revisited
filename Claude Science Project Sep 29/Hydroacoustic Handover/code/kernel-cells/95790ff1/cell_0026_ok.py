import numpy as np
pg=doc[22]
imgs=[o for o in pg.get_objects() if o.type==pdfium.raw.FPDF_PAGEOBJ_IMAGE]
for k,o in enumerate(imgs):
    b=o.get_bitmap(render=False).to_pil(); print(k, b.size, b.mode, o.get_pos() if hasattr(o,'get_pos') else o.get_bounds() if hasattr(o,'get_bounds') else '')
    b.save(f"crops/p23_img{k}.png")