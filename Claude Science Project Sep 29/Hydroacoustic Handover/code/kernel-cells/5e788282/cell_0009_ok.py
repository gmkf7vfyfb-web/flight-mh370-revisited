import shutil
r=pdf_pages(P, mode="image", pages=[4,5], dpi=200)
for p in r: print(p['page'], p['image_path'])
from PIL import Image
im=Image.open(r[1]['image_path']); print(im.size)
host.view_image(r[1]['image_path'])