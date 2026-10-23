K19="articles/10.1038_s41598-018-37626-z.pdf"
pk=pdf_pages(K19, mode="text")
with open("kadri2019_text.txt","w") as f:
    for p in pk: f.write(f"\n── page {p['page']} ──\n{p['text']}")
print(len(pk), os.path.getsize("kadri2019_text.txt"))
kd=fitz.open(K19)
for i,pg in enumerate(kd):
    print(i+1, len(pg.get_drawings()), [(x['width'],x['height']) for x in pg.get_image_info()])