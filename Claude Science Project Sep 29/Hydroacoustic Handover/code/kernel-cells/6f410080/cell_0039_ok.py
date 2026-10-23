d=fitz.open('mrsa_map_26mar2014.pdf')
pg=d[2]; pix=pg.get_pixmap(dpi=300); pix.save('mrsa_p2_hi.png'); print(pix.width,pix.height)
# list embedded images
print(pg.get_images())
for img in pg.get_images():
    x=d.extract_image(img[0]); print(x['width'],x['height'],x['ext'])
    open(f"mrsa_p2_img.{x['ext']}",'wb').write(x['image'])