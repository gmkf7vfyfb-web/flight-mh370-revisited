import fitz, numpy as np, collections
fd=fitz.open(P)
for pno in [3,4,1,6]:
    pg=fd[pno]; drw=pg.get_drawings()
    cc=collections.Counter()
    for d in drw:
        col=tuple(round(x,3) for x in d['color']) if d.get('color') else None
        fill=tuple(round(x,3) for x in d['fill']) if d.get('fill') else None
        cc[(col,fill,len(d['items'])>20)]+=1
    print("page",pno+1,len(drw))
    for k,v in cc.most_common(25): print("  ",k,v)
    print("  images:",[ (i[0], fd.extract_image(i[0])['width'], fd.extract_image(i[0])['height']) for i in pg.get_images()], [pg.get_image_bbox(i) for i in pg.get_images()])